#include <Wire.h>

#define WINDOW_SIZE 10
#define SERIAL_NOT_I2C 0

const byte ledPin = 13;
const byte interruptPin = 2;
volatile int state = 0;
volatile int flag = 0;
volatile long oldTime = 0;
volatile long newTime = 0;
int address = 11;

union Buffer
{
  unsigned long deltaMicroSeconds;
  byte longBytes[4];
};

Buffer buffer;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(interruptPin, INPUT_PULLUP);
  if (SERIAL_NOT_I2C) {
    Serial.begin(2000000);
  } else {
    Wire.begin(address);
    Wire.onRequest(requestEvent);
  }
  attachInterrupt(digitalPinToInterrupt(interruptPin), risingEdge, RISING);
}

void loop() {
  if (flag == 1) {
    buffer.deltaMicroSeconds = newTime - oldTime;
    if (SERIAL_NOT_I2C) {
      Serial.println(buffer.deltaMicroSeconds);
    }
    oldTime = newTime;
    flag = 0;
    if (!SERIAL_NOT_I2C) {
    	delay(1); //This is needed because otherwise I2C doesn't work. Something about enough time for overhead.
    }
  }
}

void requestEvent() {
  Wire.write(buffer.longBytes, 4);
}

void risingEdge() {
  state = digitalRead(interruptPin);
  newTime = micros();
  flag = 1;
}
