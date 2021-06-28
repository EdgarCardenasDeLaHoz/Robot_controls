

/*
  Op3Mech controller

  Designed to be used with the CNC shield V3.

  Created 26/07/2020

  By Jona Gladines
  For Op3Mech
*/

#include <SoftwareSerial.h>                         //libraries for the processing of the serial command and to controll the stepper motors
#include <SerialCommand.h>
#include <AccelStepper.h>

SerialCommand SCmd;                                 // The SerialCommand object

AccelStepper steppers[4] = {
  AccelStepper(AccelStepper::DRIVER, 2, 5),
  AccelStepper(AccelStepper::DRIVER, 3, 6),
  AccelStepper(AccelStepper::DRIVER, 4, 7)
};

int stepperEnablePin = 8;                           //pin to enable stepper drivers on the CNC shield,must be tied low to enable drivers
int uddir = 1;
unsigned long lastMillis;
bool b_move_complete = true;

void setup() {

  pinMode(stepperEnablePin, OUTPUT);
  digitalWrite(stepperEnablePin, LOW);

  for (int i = 0; i <= 3; i++) {                    //set the maximum speed and acceleration for the stepper motors
    steppers[i].setMaxSpeed(25000);
    steppers[i].setAcceleration(10000);
  }

  SCmd.addCommand("M", move_stepper);
  SCmd.addCommand("V", change_velocity);
  SCmd.addCommand("STOP", stop_all);
  SCmd.addCommand("Info", send_info);
  SCmd.addCommand("Pos", send_position);
  SCmd.addCommand("R", check_move_complete);
  SCmd.addDefaultHandler(unrecognized);

  Serial.begin(9600);
  Serial.println("Robotic Arm");
  //
}

void loop() {
  SCmd.readSerial();                             //check if there are serial commands, if so, process them
  for (int i = 0; i <= 3; i++) {                    //set the maximum speed and acceleration for the stepper motors
    steppers[i].run();
  }


  if (millis() - lastMillis >= 2 * 60 * 1000UL) {
    lastMillis = millis();  //get ready for the next iteration
    check_move_complete();
  }
}

// This gets set as the default handler, and gets called when no other command matches.
void unrecognized()
{
  Serial.println("Not recognized");            //returns not ok to software

}


void send_info() {
  Serial.println("Robot Arm");
}


void send_position() {
  Serial.println("Robot Arm");
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

void stop_all() {
  for (int i = 0; i <= 3; i++) {
    steppers[i].move(0);
  }
}


void move_stepper() {

  char *arg;
  int step_idx;
  float distance;

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

  arg = SCmd.next();
  if (arg == NULL)   {
    Serial.println("Not recognized: No hieght parameter given");
    return;
  }

  distance = atof(arg);
  if (distance == 0) {
    Serial.println("Not recognized: Height parameter not parsed");
    return;
  }

  Serial.print("moving ");
  Serial.print(distance);
  Serial.println(" Degrees");

  distance = distance * 32 * 2.778;
  steppers[step_idx].move(distance);
  b_move_complete = false;


}
