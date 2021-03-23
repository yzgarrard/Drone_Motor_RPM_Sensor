import smbus2
import time
import struct  # TODO: Check if I need this library
import ctypes  # TODO: Check if I need this library
import csv
import sched

# I2C bus. As far as I can tell, there is only 1 I2C bus available on the RPi.
bus = smbus2.SMBus(1)
# Address of the Arduino  Nano.
# address = 11
# Put the number of motor poles here.
motorPoles = 14
# Constant to convert time between two rising edges on a BLDC motor lead to RPM.
deltaMicrosToRPMConstant = (60 * 1000 * 1000) / (motorPoles / 2)

prev_poll_time = 1
sampleFrequency = 200  # Number of samples to (try to) take every second.
timeOffset = time.time()    # Used to get the first sample time close to 0.


def i2c_read_delta_micros(address: int) -> int:
    """
    Grabs 4 bytes of data from device at address using I2C.
    :param address: Address of device. Don't add read/write bit.
    :return: If positive, returns the time between the two most recent consecutive rising edges. If negative, then the
    I2C transaction failed.
    """
    try:
        # grabs four bytes of data from target at address. Not sure what the 0 is for, maybe offset.
        block = bus.read_i2c_block_data(address, 0, 4)
        # Append data into a long data type.
        delta_micros = (block[3] << 24) + (block[2] << 16) + (block[1] << 8) + block[0]
    except OSError:
        # Since good data will always be positive, a negative value is a check to validate said data.
        delta_micros = -1
    return delta_micros


def calculate_rpm(delta_micros: int) -> float:
    """
    Computes the RPM using the rising-edge to rising-edge time.
    :param delta_micros: Time between two consecutive rising edges.
    :return: RPM of the motor
    """
    return deltaMicrosToRPMConstant / delta_micros


def record_data():
    with open("data.csv", "a", newline="") as dataFile:
        data_writer = csv.DictWriter(dataFile, fieldnames=fieldNames)

        # If the data is bad, don't record it.
        delta_micros = i2c_read_delta_micros(12)
        if delta_micros < 0:
            return
        rpm = calculate_rpm(delta_micros)
        #print(rpm)
        current_time = time.time() - timeOffset
        poll_dt = current_time - prev_poll_time
        data_writer.writerow({"time": current_time,  # sample timestamp in s
                              "edge_dt": delta_micros,  # time between two consecutive rising edges
                              "calc_RPM": rpm,  # calculated RPM
                              "poll_dt": poll_dt})  # time between samples in s


def poll_data(s: sched.scheduler):
    s.enter(1 / sampleFrequency, 5, poll_data, kwargs={"s": s})  # Schedule a sample to be taken at desired frequency.
    record_data()


if __name__ == "__main__":
    # This bit sets up the csv file for data collection.
    with open("data.csv", "w", newline="") as dataFile:
        # time is the sample timestamp in seconds. edge_dt is the time between two rising edges in microseconds.
        # calc_RPM is the calculated RPM. poll_dt is how long it's been since the last poll in milliseconds.
        fieldNames = ["time", "edge_dt", "calc_RPM", "poll_dt"]
        dataWriter = csv.DictWriter(dataFile, fieldnames=fieldNames)
        dataWriter.writeheader()

    #  Creates a scheduler following the example from https://docs.python.org/3/library/sched.html
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(1 / sampleFrequency, 5, poll_data, (scheduler,))
    scheduler.run()
