#include <SimpleStepper.h>

SimpleStepper stepper1(96, 2, 5);
int enablePin = 8;


void setup() {
  // put your setup code here, to run once:
  stepper1.setSpeed(200);
  stepper1.setRevs(20);
  pinMode(enablePin, OUTPUT);
  digitalWrite(enablePin, LOW);
  pinMode(1, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  stepper1.run();
}
