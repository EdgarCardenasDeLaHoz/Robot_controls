#include <AccelStepper.h>

AccelStepper steppers[4] = {
  AccelStepper(AccelStepper::DRIVER, 2, 5),
  AccelStepper(AccelStepper::DRIVER, 3, 6),
  AccelStepper(AccelStepper::DRIVER, 4, 7),
  AccelStepper(AccelStepper::DRIVER, 12, 13)
};

int leds[] = {14, 15, 16, 17};

int stepperEnablePin = 8;
int buttonS = 9;
int buttonU = 10;
int buttonD = 11;

int selectedStepper = 0;
int uddir = 0;
int speedTable[] = {50, 250, 500};
bool upDownPressed = false;
bool upDownPreviousState = false;
bool selectPreviousState = false;
bool stepperEnable = true;

long upDownButtonPressTime = 0;
int longPressTime = 1000;

void setup(){

  steppers[0].setMaxSpeed(500);
  steppers[0].setAcceleration(2000);

  steppers[1].setMaxSpeed(500);
  steppers[1].setAcceleration(2000);

  steppers[2].setMaxSpeed(500);
  steppers[2].setAcceleration(2000);

  steppers[3].setMaxSpeed(500);
  steppers[3].setAcceleration(2000);
  
  pinMode(buttonS, INPUT_PULLUP);
  pinMode(buttonU, INPUT_PULLUP);
  pinMode(buttonD, INPUT_PULLUP);

  pinMode(leds[0], OUTPUT);
  pinMode(leds[1], OUTPUT);
  pinMode(leds[2], OUTPUT);
  pinMode(leds[3], OUTPUT);

  pinMode(stepperEnablePin, OUTPUT);

  animation();
  
  digitalWrite(leds[selectedStepper], HIGH);
  digitalWrite(stepperEnablePin, LOW);
  Serial.begin(9600);
  
}

void loop(){

  checkInput();
  int mySpeed = calculateSpeed();
  if(upDownPressed){
    //Serial.println("go");
    steppers[selectedStepper].setSpeed(uddir*mySpeed);
    steppers[selectedStepper].runSpeed();
  }
  //steppers[0].run();
  //steppers[1].run();
  //steppers[2].run();
  //steppers[3].run();
  
}

void checkInput(){
  int val=0;
  val += digitalRead(buttonS)*1;
  val += digitalRead(buttonU)*2;
  val += digitalRead(buttonD)*4;
  
  switch(val){
    case 6:       //button S pressed
                  if(selectPreviousState==false){
                    digitalWrite(leds[selectedStepper], LOW);
                    selectedStepper++;
                    if(selectedStepper==4){ selectedStepper = 0; }
                    digitalWrite(leds[selectedStepper], HIGH);
                    selectPreviousState=true;
                  }
                  break;

    case 5:       //button U pressed
                  uddir=-1;
                  upDownPressed=true;
                  //steppers[selectedStepper].moveTo(-20000);
                  //Serial.println(upDownButtonPressTime);
                  break;

    case 3:       //button D pressed
                  uddir=1;
                  upDownPressed=true;
                  //steppers[selectedStepper].moveTo(20000);
                  //Serial.println(upDownButtonPressTime);
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
    if(pressTime > 2500)
      speedStep=2;
    else if(pressTime > 1500)
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

void animation(){
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
