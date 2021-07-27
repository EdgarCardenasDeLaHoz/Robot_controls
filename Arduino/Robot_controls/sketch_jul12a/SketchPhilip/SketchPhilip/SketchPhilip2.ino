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
#include <Stepper.h>

SerialCommand SCmd;                                 // The SerialCommand object

//AccelStepper steppers[4] = {
 // AccelStepper(AccelStepper::DRIVER, 2, 5),
  //AccelStepper(AccelStepper::DRIVER, 3, 6),
  //AccelStepper(AccelStepper::DRIVER, 4, 7)
//};

int stepperEnablePin = 8;                           //pin to enable stepper drivers on the CNC shield,must be tied low to enable drivers
int uddir = 1;
unsigned long lastMillis;
bool b_move_complete = true;

#define FULLSTEP 4

AccelStepper myStepper1(FULLSTEP, 9, 11, 10, 12);
AccelStepper myStepper2(FULLSTEP, 4, 6, 5, 7);

void setup() {

  myStepper1.setMaxSpeed(10000.0);
  myStepper1.setAcceleration(150.0);
  myStepper1.setSpeed(10000.0);
  
  
  myStepper2.setMaxSpeed(10000.0);
  myStepper2.setAcceleration(100.0);
  myStepper2.setSpeed(10000.0);
  
  //pinMode(stepperEnablePin, OUTPUT);              //this is for nema's
  //digitalWrite(stepperEnablePin, LOW);

  // for (int i = 0; i <= 3; i++) {                    //set the maximum speed and acceleration for the stepper motors
    //steppers[i].setMaxSpeed(25000);
    //steppers[i].setAcceleration(10000);
  //}

  SCmd.addCommand("M", move_stepper);
  //SCmd.addCommand("V", change_velocity);
  //SCmd.addCommand("STOP", stop_all);
  //SCmd.addCommand("Info", send_info);
  //SCmd.addCommand("Pos", send_position);
  //SCmd.addCommand("R", check_move_complete);
  //SCmd.addDefaultHandler(unrecognized);

  Serial.begin(9600);
  Serial.println("Microscope");
  //
}

void loop() {
   //check if there are serial commands, if so, process them
   SCmd.readSerial(); 
   /*                                                
  for (int i = 0; i <= 3; i++) {                    //set the maximum speed and acceleration for the stepper motors
    steppers[i].run();
   
  }


  if (millis() - lastMillis >= 2 * 60 * 1000UL) {
    lastMillis = millis();  //get ready for the next iteration
    check_move_complete();
  }
  */
}

// This gets set as the default handler, and gets called when no other command matches.
void unrecognized()
{
  Serial.println("Not recognized");            //returns not ok to software

}
void test(){
  
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
    Serial.println("Not recognized: No height parameter given");
    return;
  }

  distance = atof(arg);
  if (distance == 0) {
    Serial.println("Not recognized: Height parameter not parsed");
    return;
  }
  distance = distance * 32 * 2.778;
  Serial.print("moving");
  Serial.print(distance);
  Serial.println("Degrees");
  
  
  if (step_idx == 2) {
    for (int i = 0; i <= distance; i++) { 
    myStepper1.move(1);
    myStepper1.run();
    delay(10);
    }
  }
  
  if (step_idx == 3) {
    for (int i = 0; i <= distance; i++) { 
    myStepper2.move(1);
    myStepper2.run();
    delay(10);
    }
  }
  
  b_move_complete = false;


}

void send_info() {
  Serial.println("Microscope");
}


/*void change_velocity()    //function called when a serial command is received
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
*/
/*void check_move_complete() {


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
*/

/*void stop_all() {
  for (int i = 0; i <= 3; i++) {
    steppers[i].move(0);
  }
}
*/
