
/*
  Op3Mech controller

  Designed to be used with the CNC shield V3.

  Created 28/04/2021

  By Olivier De Moor & Edgar Cardenas
  For InViLab
*/
#include <Servo.h>
#include <SoftwareSerial.h>   
#include <SerialCommand.h>
#include <AccelStepper.h>

SerialCommand SCmd; 


AccelStepper steppers[4] = {
  AccelStepper(AccelStepper::DRIVER, 2, 5),
  AccelStepper(AccelStepper::DRIVER, 3, 6),
  AccelStepper(AccelStepper::DRIVER, 4, 7)
  };

float pitch = 8.00;   
float spr = 200;  
int stepperEnablePin = 8;  
int uddir = 1; 
unsigned long lastMillis;
bool b_move_complete = true;


void setup() {
  // put your setup code here, to run once:

   pinMode(stepperEnablePin, OUTPUT);
  digitalWrite(stepperEnablePin, LOW);

  for (int i = 0; i <= 3; i++) {                    //set the maximum speed and acceleration for the stepper motors
    steppers[i].setMaxSpeed(500);
    steppers[i].setAcceleration(500);
  }
 Serial.begin(9600);
  SCmd.addCommand("Info",send_info);
  SCmd.addCommand("M",move_stepper);
  SCmd.addCommand("V", change_velocity);
  SCmd.addCommand("R", check_move_complete);
  SCmd.addDefaultHandler(unrecognized);
    Serial.println("Scara");   
}

void loop() {
  // put your main code here, to run repeatedly:
SCmd.readSerial();
  for (int i = 0; i <= 3; i++) {                    //set the maximum speed and acceleration for the stepper motors
    steppers[i].run();
  }

  
  if (millis() - lastMillis >= 2 * 60 * 1000UL) {
    lastMillis = millis();  //get ready for the next iteration
    check_move_complete();
  }
}
void unrecognized()
{
  Serial.println("Not recognized");            //returns not ok to software
  Serial.println("Ready");
 
}
void send_info(){
  Serial.println("Scara");  
}
void check_move_complete() {


  if (b_move_complete) {
    Serial.println("Ready for next command");
    return;
  }

  bool b_all_done = true;
  for (int i = 0; i <= 3; i++) {
    if (steppers[i].distanceToGo() > 0) {
      b_all_done = false;
    }
  }

  if (b_all_done) {
    Serial.println("Ready for next command");
    b_move_complete = true;
  }
  else {
    Serial.println("Busy");
  }

}
void change_velocity()    //function called when a serial command is received
{
  char *arg;
  float velocity;

  arg = SCmd.next();
  if (arg == NULL) {
    Serial.println("Not recognized: No Velocity given");
    return;
  }
    velocity = atoi(arg);
  if (velocity == 0) {
    Serial.println("Not recognized: Velocity parameter could not get parsed");
    return;
  }
    for (int i = 0; i <= 3; i++) {
    steppers[i].setMaxSpeed(velocity);
  }

}
void move_stepper()    //function called when a serial command is received
{

  float height; 
  int step_idx; 
  char *arg; 

    arg = SCmd.next();
  if (arg == NULL)  {
    Serial.println("Not recognized: Stepper Number" );
    return;
  }

  step_idx = atoi(arg);
  if (step_idx < 0) {
    Serial.print("Not recognized:");   Serial.println(step_idx);  return;

    Serial.print("ID ");
    Serial.print(step_idx );
  }

  arg = SCmd.next();                                                //select next argument
  if (arg != NULL) {                                                //throw error if there is no new argument
    height=atof(arg);                                               //height as a floating value is parsed
    if(height != 0){                                                //if there are no errors in parsing, there is a proper value
      Serial.print("moving ");
      Serial.print(height);
      Serial.println("mm");
      //stepper.move();     //calculate the amount of steps to be taken with the steps per revolution, the pitch and the height
      steppers[step_idx].setCurrentPosition(0);
      steppers[step_idx].runToNewPosition(round((height/pitch)*spr));
    }
    else{
      Serial.println("Not recognized: Height parameter could not get parsed");     // height was not correctly parsed
    }
  } 
  else {
        Serial.println("Not recognized: No hieght parameter given");       // no heigt given
  }
  
  Serial.println("Ready");
}
