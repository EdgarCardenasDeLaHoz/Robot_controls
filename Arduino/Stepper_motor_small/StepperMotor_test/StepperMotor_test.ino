#include <Stepper.h>

const float Steps_per_rev = 32;
const float Gear_red = 64; 
const float Steps_per_out_rev = Steps_per_rev*Gear_red; 

int StepsRequired;

Stepper steppermotor(Steps_per_rev, 9, 10, 11, 12);


int step_number = 0; 

void setup() {
}

void loop() {
  
  steppermotor.setSpeed(1);
  StepsRequired = 4;
  steppermotor.step(StepsRequired); 
  delay(2000);

  StepsRequired = Steps_per_out_rev / 2;
  steppermotor.setSpeed(100);
  steppermotor.step(StepsRequired);
  delay(1000);

  StepsRequired = -Steps_per_out_rev / 2;
  steppermotor.setSpeed(700);
  steppermotor.step(StepsRequired);
  delay(2000);
}
