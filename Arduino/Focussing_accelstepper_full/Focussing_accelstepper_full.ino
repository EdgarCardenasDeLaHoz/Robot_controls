/*
  Op3Mech Stratinvest Focussing controller

  Designed to be used with the CNC shield V3. It controlles up to 4 stepper motors via
  pushbuttons on the front panel or via serial command  over RS232

  The front panel has 3 switches connected to ground INPUT_PULLUP is used to avoid extra external components
  1. Select switch: used to select the stepper motor. connected to the X-axis endstop of the CNC shield (aka pin 9 on the arduino)
  2. Up switch: used to control the selected stepper motor CCW. connected to the Y-axis endstop of the CNC shield (aka pin 10 on the arduino)
  3. Down switch: used to control the selected stepper motor CW. connected to the Z-axis endstop of the CNC shield (aka pin 11 on the arduino)

  The front panel has 4 LED's connected to "resume", "hold", "abort" and "coolant enable" of the CNC shield (aka pins A0, A1, A2, A3, but named 14, 15, 16, 17 if used digtally)

  Serial commands are build up as follows
  F "stepper number" "height to travel"
  e.g. "F 2 5.3"

  Created 13/02/2019
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
  AccelStepper(AccelStepper::DRIVER, 4, 7),
  AccelStepper(AccelStepper::DRIVER, 12, 13)
};                                                  //Create array of 4 stepper motors attached through drivers on the pins for the X, Y, Z and A axis of the CNC shield

int leds[] = {14, 15, 16, 17};                      //leds to show the selected stepper.
float pitch[] = {3.98, 3.98, 3.98, 3.98};           //z-axis pitch of the z-axis mount in mm/Rev. can be set to different vallues for different mount if used that way
float spr[] = {200, 200, 200, 200};                 //steps per revolution for each stepper motor

int stepperEnablePin = 8;                           //pin to enable stepper drivers on the CNC shield,must be tied low to enable drivers
int buttonS = 9;                                    //pin on arduino to select the stepper
int buttonU = 10;                                   //pin on arduino for the up button
int buttonD = 11;                                   //pin on arduino for the down button

int selectedStepper = 0;                            //hols the currently selected stepper ranging from 0 to 3 
int uddir = 1;                                      //sets the direction for the motor when using the speed controll
int speedTable[] = {50, 250, 500};                  //speeds in steps/min for the speed increase while manually focussing
bool upDownPressed = false;                         //set to true when the up or down buttons are pressed.
bool upDownPreviousState = false;                   //holds the prefious state of the up down button to detect changes
bool selectPreviousState = false;                   //holds the previous state for the select button to detect changes
//bool stepperEnable = true;  

long upDownButtonPressTime = 0;                     //holds the initial time the up or down button was pressed to know how long the button was pressed
//int longPressTime = 1000;

int lastButtonCount = 7;                            //holds the previous total of buttons pressed to detect changes and to debounce
unsigned long lastDebounceTime = 0;                 //the last time the output was set
unsigned long debounceDelay = 50;                   //the debounce time; increase if the output flickers
int buttonState;                                    //holds the current button state

void setup(){

  for(int i=0; i<=3; i++){                          //set the maximum speed and acceleration for the stepper motors
    steppers[i].setMaxSpeed(500);
    steppers[i].setAcceleration(2000);
    pinMode(leds[i], OUTPUT);
  }

  pinMode(buttonS, INPUT_PULLUP);                   //configure pins with switches as input with internal pullup so no external resistor needs to be used
  pinMode(buttonU, INPUT_PULLUP);
  pinMode(buttonD, INPUT_PULLUP);

  pinMode(stepperEnablePin, OUTPUT);                //set the enable pin as an output

  animation();                                      //run the startup animation to verify all leds are working.
  
  digitalWrite(leds[selectedStepper], HIGH);        //show on the LED's which is the currently selected stepper
  digitalWrite(stepperEnablePin, LOW);              //enable all stepper drivers
  Serial.begin(9600);                               //start the serial commanding        

  SCmd.addCommand("F",processFocus);                // takes the camera parameter and the height and processes the focus job. 
  SCmd.addDefaultHandler(unrecognized);             // Handler for command that isn't matched  (says "What?") 
  Serial.println("Ready");                          // Return ready on the serial bus for the software to know when the controller is ready to recieve data.
}

void loop(){
  
  checkInput();                                     //check the input of the push buttons
  SCmd.readSerial();                                //check if there are serial commands, if so, process them
  if(upDownPressed){                                //if the up or down button is depressed
    int mySpeed = calculateSpeed();                           //calculate the speed based on the press time
    steppers[selectedStepper].setSpeed(uddir*mySpeed);        //set the speed for speed control, negative speeds means that the motor turns in the other direction
    steppers[selectedStepper].runSpeed();                     //tell the motor to take a step
    steppers[selectedStepper].setCurrentPosition(0);          //tell the library that the new position is the new 0.
  }
  else{                                             // if no button is pressed, tell the steppers to take a step if there is a step to be taken from a serial command.
    steppers[0].run();
    steppers[1].run();
    steppers[2].run();
    steppers[3].run();
  }
  
}

void checkInput(){
  int buttonCount=0;                               //start button countas 0, each button has a wheight so we can destinguish when multiple buttons are pressed simultaniously
                                                   // similar to linux file permissions for read(4), write(2) and execute(1)
  buttonCount += digitalRead(buttonS)*1;           //select button has wheight 1
  buttonCount += digitalRead(buttonU)*2;           //up button has wieght 2
  buttonCount += digitalRead(buttonD)*4;           //down button has weight 4

  if(buttonCount != lastButtonCount)               //every time te buttons change state, the last debounce time is updated
  {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {      //if the current time - the last debounce time is larger than the debounce delay, the bouncing should have stopped

    // if the button state has changed:
    if (buttonCount != buttonState) {                       //only act if the buttonstate is changed.
      buttonState = buttonCount;
      switch(buttonState){                                  //switch the current button state
        case 6:       if(selectPreviousState==false){                     //button S pressed
                        digitalWrite(leds[selectedStepper], LOW);         //disable the current stepper LED
                        selectedStepper++;                                //change the selected stepper  
                        if(selectedStepper==4){ selectedStepper = 0; }    //if the count is 4 resest it to 0
                        digitalWrite(leds[selectedStepper], HIGH);        //enable the new stepper LED
                        selectPreviousState=true;                         
                      }                                                   
                      break;                                              

    
        case 5:       uddir=1;                                            //button U pressed
                      upDownPressed=true;
                      break;

        case 3:       uddir=-1;                                           //button D pressed
                      upDownPressed=true;
                      break;

                      
        default:      // default condition when no or multiple buttons are pressed used to reset all button states.
                      selectPreviousState=false;
                      upDownPressed=false;
                      upDownPreviousState = false;
                      break;
      }
    }
  }
  lastButtonCount = buttonCount;
}

int calculateSpeed(){
   int speedStep = 0;                                                   //default speed is step 0 --> slowest
   
   if(upDownPressed==true && upDownPreviousState==true){                //if the button is continuously pressed
    int pressTime=millis()-upDownButtonPressTime;                       //calculate how long the button is pressed
    if(pressTime > 2500)                                                //if pressed for 2.5 secondstake step 2  --> fastest
      speedStep=2;
    else if(pressTime > 1500)                                           //if pressed for 1.5 seconds take step 1
      speedStep=1;
  } else if(upDownPressed==true && upDownPreviousState==false){
    upDownButtonPressTime = millis();                                   // if the up or down button is pressed for the first time update the upDownButtonPressTime with the current time
    upDownPreviousState = true;                                         // tell the software that the button press was detected.
  } else {
    upDownPressed=false;                                                //if not pressed, reset all variables
    upDownPreviousState = false;
  }
  return speedTable[speedStep];                                         //return the speed from the array
}

void processFocus()    //function called when a serial command is received
{
  int camera;
  float height;  
  char *arg; 

  arg = SCmd.next(); 
  if (arg != NULL) {                                                    //throw error if there are no arguments
    camera=atoi(arg);                                                   // first argument is the camera/stepper number (1, 2, 3, 4)
    if(camera != 0 && camera < 5 ){                                     // if the camera value is properly send, continue, else throw error
      digitalWrite(leds[selectedStepper], LOW);                         //disable the LED of the currently selected stepper
      selectedStepper=camera-1;                                         //correction of transferred value as index goes from 0 to 3 and assign to the selected steper
      digitalWrite(leds[selectedStepper], HIGH);                        //enable the LED of the new selected stepper
      arg = SCmd.next();                                                //select next argument
      if (arg != NULL) {                                                //throw error if there is no new argument
        height=atof(arg);                                               //height as a floating value is parsed
        if(height != 0){                                                //if there are no errors in parsing, there is a proper value
           steppers[selectedStepper].move(round((height/pitch[selectedStepper])*spr[selectedStepper]));     //calculate the amount of steps to be taken with the steps per revolution, the pitch and the height
        }
        else{
          Serial.println("NOK1");     // height was not correctly parsed
        }
      } 
      else {
        Serial.println("NOK2");       // no heigt given
      }
    }
    else{
      Serial.println("NOK3");         // camera was not correctly parsed
    }
  } 
  else {
    Serial.println("NOK4");           // no parameters given.
  }

}

// This gets set as the default handler, and gets called when no other command matches. 
void unrecognized()
{
  Serial.println("NOK5");            //returns not ok to software
}






void animation(){               //playing startup animation loops all leds twice and then enables all leds before disabeling them all.
  int i=14;
  for(i=14; i<=17; i++)
  {
    digitalWrite(i, LOW);
  }

  for(i=14; i<=17; i++)
  {
    digitalWrite(i, HIGH);
    if(i>14)
    {
      digitalWrite(i-1, LOW);
    }
    delay(100);
  }

  for(i=16; i>=14; i--)
  {
    digitalWrite(i, HIGH);
    digitalWrite(i+1, LOW);
    delay(100);
  }

  for(i=14; i<=17; i++)
  {
    digitalWrite(i, HIGH);
    if(i>14)
    {
      digitalWrite(i-1, LOW);
    }
    delay(100);
  }

  for(i=16; i>=14; i--)
  {
    digitalWrite(i, HIGH);
    digitalWrite(i+1, LOW);
    delay(100);
  }

  for(i=14; i<=17; i++)
  {
    digitalWrite(i, HIGH);
    delay(100);
  }
  delay(600);

  for(i=14; i<=17; i++)
  {
    digitalWrite(i, LOW);
  }

}
