#include <Wire.h>

#define WINDOW_SIZE 10
#define SERIAL_PRINT 0	// ONLY SET THIS TO 1 FOR DEBUG PURPOSES! IT'S VERY EXPENSIVE
#define I2C_WRITE 1

const byte interruptPin = 2;
volatile int flagRecord = 0; //To indicate that a new measurement has been taken, and that the main loop has to do a time difference calculation.11
volatile int consecutiveMeasurementCount = 0;	//Counts the number of consecutive measurements taken after the last I2C poll.
volatile long oldTime = 0;
volatile long newTime = 0;
int address = 11;

// A union is used because it stores the same data in ways that makes it convenient to write to as an unsigned long and easy to write over I2C as bytes.
union Buffer
{
  unsigned long deltaMicroSeconds;
  byte longBytes[4];
} buffer;

void setup() {
	pinMode(interruptPin, INPUT_PULLUP);	// For Arduino Nano, this is pin  D2. I'm unsure is pullup or pulldown are important.
	if (SERIAL_PRINT) {
		Serial.begin(2000000);
	}
	if (I2C_WRITE) {
		Wire.begin(address);
		Wire.onRequest(requestEvent);
	}
	TWAR = 0x77 << 1;	// Disable I2C until I have data to send
	attachInterrupt(digitalPinToInterrupt(interruptPin), risingEdge, RISING); // When rising edges occur on the interrupt bin, run function "risingEdge()".
}

void loop() {
  if (flagRecord == 1) {	// Only run computations if there is new data.
    buffer.deltaMicroSeconds = newTime - oldTime;
    if (SERIAL_PRINT) {
      Serial.print(buffer.deltaMicroSeconds);
      Serial.print(" ");
      Serial.println(consecutiveMeasurementCount);
    }
    oldTime = newTime;
    flagRecord = 0;
    if (++consecutiveMeasurementCount >= 2) {
		TWAR = address << 1;	//Resume I2C to permit data transmission.
    }
    /*if (I2C_WRITE) {
    	delay(1); //This is needed because otherwise I2C doesn't work. Something about enough time for overhead.
    }*/
  }
}

void requestEvent() {
  Wire.write(buffer.longBytes, 4);
  consecutiveMeasurementCount = 0;
  Serial.println(TWCR);
  TWAR = 0x77 << 1;	// Disable I2C exchanges by changing address.
  Serial.println(TWCR);
}

void risingEdge() {
  newTime = micros();
  flagRecord = 1;
}
