#include <SoftwareSerial.h> 
#include <SerialCommand.h>
#include<SimpleStepper.h>

SerialCommand SCmd;   // The SerialCommand object

SimpleStepper steppers[4] = {
  SimpleStepper(200, 2, 5),
  SimpleStepper(200, 3, 6),
  SimpleStepper(200, 4, 7),
  SimpleStepper(200, 12, 13)
};

int leds[] = {14, 15, 16, 17};      //leds to show the selected stepper.
float pitch[] = {2.0, 2.0, 2.0, 2.0};  //z-axis pitch in mm/Rev.

int stepperEnablePin = 8;
int buttonS = 9;
int buttonU = 10;
int buttonD = 11;

int selectedStepper = 0;
int uddir = 0;
int speedTable[] = {145, 110, 80, 55, 35, 20, 10, 5};
bool upDownPressed = false;
bool upDownPreviousState = false;
bool selectPreviousState = false;
bool stepperEnable = true;

int upDownButtonPressTime = 0;
int longPressTime = 1000;

void setup(){
  pinMode(buttonS, INPUT_PULLUP);
  pinMode(buttonU, INPUT_PULLUP);
  pinMode(buttonD, INPUT_PULLUP);

  pinMode(leds[0], OUTPUT);
  pinMode(leds[1], OUTPUT);
  pinMode(leds[2], OUTPUT);
  pinMode(leds[3], OUTPUT);

  pinMode(stepperEnablePin, OUTPUT);
  
  digitalWrite(leds[selectedStepper], HIGH);
  digitalWrite(stepperEnablePin, LOW);
  Serial.begin(9600);

  SCmd.addCommand("F",processFocus);    // takes the camera parameter and the height and processes the focus job. 
  SCmd.addDefaultHandler(unrecognized);          // Handler for command that isn't matched  (says "What?") 
  Serial.println("Ready");
  
}

void loop(){
  
  SCmd.readSerial();     // We don't do much, just process serial commands
  checkInput();
  int mySpeed = calculateSpeed();
  if(upDownPressed){
    steppers[selectedStepper].setSpeed(mySpeed);
    if(uddir==0)
      steppers[selectedStepper].setSteps(1);
    else
      steppers[selectedStepper].setSteps(-1);
  }
  steppers[0].run();
  steppers[1].run();
  steppers[2].run();
  steppers[3].run();
  
}

void checkInput(){
  int val=0;
  val += digitalRead(buttonS)*1;
  val += digitalRead(buttonU)*2;
  val += digitalRead(buttonD)*4;
  
  switch(val){
    case 1:       //button S pressed
                  if(selectPreviousState==false){
                    Serial.println("Button S");
                    digitalWrite(leds[selectedStepper], LOW);
                    selectedStepper++;
                    if(selectedStepper==4){ selectedStepper = 0; }
                    digitalWrite(leds[selectedStepper], HIGH);
                    selectPreviousState=true;
                  }
                  break;

    case 2:       //button U pressed
                  Serial.println("Button U");
                  uddir=0;
                  upDownPressed=true;
                  break;

    case 4:       //button D pressed
                  Serial.println("Button D");
                  uddir=1;
                  upDownPressed=true;
                  break;
                  
    default:      // default condition when no or multiple buttons are pressed
                  selectPreviousState=false;
                  upDownPressed=false;
                  upDownPreviousState = false;
                  break;
  }

}

int calculateSpeed(){
   int speedStep = 0;
   
   if(upDownPressed==true && upDownPreviousState==true){
    int pressTime=millis()-upDownButtonPressTime;
    if(pressTime > 3800)
       speedStep=7;
    else if(pressTime > 3600)
      speedStep=6;
    else if(pressTime > 3300)
      speedStep=5;
    else if(pressTime > 3000)
      speedStep=4;
    else if(pressTime > 2500)
      speedStep=3;
    else if(pressTime > 2000)
      speedStep=2;
    else if(pressTime > 1000)
      speedStep=1;
  } else if(upDownPressed==true && upDownPreviousState==false){
    upDownButtonPressTime = millis();
    upDownPreviousState = true;
  } else {
    upDownPressed=false;
    upDownPreviousState = false;
  }

  return speedTable[speedStep];
}

void processFocus()    
{
  int camera;
  float height;  
  char *arg; 

  arg = SCmd.next(); 
  if (arg != NULL) {
    camera=atoi(arg);    // Converts a char string to an integer
    if(camera != 0){
      selectedStepper=camera-1;
      digitalWrite(leds[selectedStepper], HIGH);
      arg = SCmd.next();
      if (arg != NULL) {
        height=atof(arg);
        if(height != 0){
           steppers[selectedStepper].setSpeed(145);
           steppers[selectedStepper].setRevs(height/pitch[selectedStepper]);
        }
        else{
          Serial.println("NOK");     // height was not correctly parsed
        }
      } 
      else {
        Serial.println("NOK");       // no heigt given
      }
    }
    else{
      Serial.println("NOK");         // camera was not correctly parsed
    }
  } 
  else {
    Serial.println("NOK");           // no parameters given.
  }

}

// This gets set as the default handler, and gets called when no other command matches. 
void unrecognized()
{
  Serial.println("NOK"); 
}
