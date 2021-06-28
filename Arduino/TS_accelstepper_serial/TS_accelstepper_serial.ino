/*
  Op3Mech translation stage controller

  Designed to be used with the CNC shield V3. It controlles 1 stepper motor via
  via serial command  over RS232

  Serial commands are build up as follows
  F  "distance to travel"
  e.g. "F 5.3"

  Created 26/07/2020
  By Jona Gladines
  For Op3Mech
*/

#include <SoftwareSerial.h>                         //libraries for the processing of the serial command and to controll the stepper motors
#include <SerialCommand.h>
#include <AccelStepper.h>

SerialCommand SCmd;                                 // The SerialCommand object

AccelStepper stepper = AccelStepper(AccelStepper::DRIVER, 2, 5);     //Create stepper motor object attached through a driver on the pins for the X axis of the CNC shield

float pitch = 8.00;         //z-axis pitch of the z-axis mount in mm/Rev. can be set to different vallues for different mount if used that way
float spr = 200;                //steps per revolution for each stepper motor

int stepperEnablePin = 8;                           //pin to enable stepper drivers on the CNC shield,must be tied low to enable drivers

int uddir = 1;                                      //sets the direction for the motor when using the speed controll

void setup(){                   
  stepper.setMaxSpeed(200);                       //set the maximum speed and acceleration for the stepper motor
  stepper.setAcceleration(1000);

  pinMode(stepperEnablePin, OUTPUT);                //set the enable pin as an output
  
  digitalWrite(stepperEnablePin, LOW);              //enable all stepper drivers
  Serial.begin(9600);                               //start the serial commanding        

  SCmd.addCommand("M",move_stepper);                // takes the camera parameter and the height and processes the focus job. 
  SCmd.addCommand("V",change_velocity); 
  SCmd.addDefaultHandler(unrecognized);             // Handler for command that isn't matched  (says "What?") 
  Serial.println("Ready");                          // Return ready on the serial bus for the software to know when the controller is ready to recieve data.
}

void loop(){
  SCmd.readSerial();                                //check if there are serial commands, if so, process them
  stepper.run();                                    //run the stepper -> if there are steps to be taken it will do so
}


void change_velocity()    //function called when a serial command is received
{
  float velocity;  
  char *arg; 

  arg = SCmd.next();                                                //select next argument
  if (arg != NULL) {                                                //throw error if there is no new argument
    velocity=atof(arg);                                               //height as a floating value is parsed
    if(velocity != 0){                                                //if there are no errors in parsing, there is a proper value
      stepper.setMaxSpeed(velocity);                                //set the maximum speed and acceleration for the stepper motor
      Serial.print(" Changing velocity to");
      Serial.println(velocity);
    }
    else{
      Serial.println("Not recognized: Velocity parameter could not get parsed");     // height was not correctly parsed
    }
  } 
  else {
        Serial.println("Not recognized: No Velocity given");       // no heigt given
  }

  
}

// This gets set as the default handler, and gets called when no other command matches. 
void unrecognized()
{
  Serial.println("Not recognized");            //returns not ok to software
  Serial.println("Ready");
}

void move_stepper()    //function called when a serial command is received
{

  float height;  
  char *arg; 

  arg = SCmd.next();                                                //select next argument
  if (arg != NULL) {                                                //throw error if there is no new argument
    height=atof(arg);                                               //height as a floating value is parsed
    if(height != 0){                                                //if there are no errors in parsing, there is a proper value
      Serial.print("moving ");
      Serial.print(height);
      Serial.println("mm");
      //stepper.move();     //calculate the amount of steps to be taken with the steps per revolution, the pitch and the height
      stepper.setCurrentPosition(0);
     stepper.runToNewPosition(round((height/pitch)*spr));
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
