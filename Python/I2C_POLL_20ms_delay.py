import smbus2
import time
import struct	# TODO: Check if I need this library
import ctypes	# TODO: Check if I need this library
import csv

bus = smbus2.SMBus(1)	# I2C bus. As far as I can tell, there is only 1 I2C bus available on the RPi.
address = 11	# Address of the Arduino  Nano.
newTime = 1	# Just some value.
oldTime = 1	# Another value. Don't choose zero otherwise there will be a division by zero error the first time the program goes.

motorPoles = 14		# Put the number of motor poles here.
deltaMicrosToRPMConstant = (60 * 1000 * 1000) / (motorPoles / 2) # Constant to convert time between two rising edges on a BLDC motor lead to RPM.


# This function grabs the last rising-edge to rising-edge time recorded on the Arduino (or whatever the Arduino will have done to the data, probably some averaging)
def getDeltaMicros():
	# Raw block of data. I can never tell what order the data comes in.
	block = bus.read_i2c_block_data(address, 0, 4)
	# Concatonate the bytes together. I think I can use the bitwise OR operator here for more performance if I really need it.
	deltaMicros = (block[3] << 24) + (block[2] << 16) + (block[1] << 8) + block[0]
	# This shouldn't happen unless the system just started or something went terribly wrong.
	if deltaMicros == 0:
		return -1


	return deltaMicros

with open("data.csv", "w", newline="") as dataFile:
	fieldNames = ["edge_dt","calc_RPM","poll_dt"] # edge_dt is the time between two rising edges in microseconds. calc_RPM is the calculated RPM. poll_dt is how long it's been since the last poll in milliseconds.
	dataWriter = csv.DictWriter(dataFile, fieldnames=fieldNames)
	dataWriter.writeheader()
	# Main program loop. TODO: replace with a scheduler to poll from the sensors at a fixed rate.
	while True:
		# I had to encapsulate everything in a try/except loop because the I2C bus occasionally failed. I'm not sure why it happens, but it's like 1 out of few hundred polls that there'll be an IOError.
		try:
			# TODO: Check which version of Python I'm using. With Python 3.7+, I think I can get a 84 (87?) ns resolution using time.time_ns() instead of what I'm currently using.
			newTime = time.monotonic_ns();
			deltaMicros = getDeltaMicros();
			print("Delta us: %6d, RPM: %4.3f, ms since last poll: %2.3f" %(deltaMicros, 8579404/deltaMicros, (newTime - oldTime)/1000000))	# delta us and ms between samples from i2c bus
			dataWriter.writerow({"edge_dt" : deltaMicros, "calc_RPM" : deltaMicrosToRPMConstant/deltaMicros, "poll_dt" : (newTime - oldTime)/1000000})
			oldTime = newTime
			time.sleep(0.010)
		except OSError as e:
			# print(time.asctime(), e)
			pass
