/*
  Stepper.cpp - A Simple Library for non blocking stepper motor use with driver board.
  Created by J. Gladines Januari 2019.
  Released into the public domain.
*/

#include "Arduino.h"
#include "SimpleStepper.h"

  SimpleStepper::SimpleStepper(int SRev, int Spin, int Dpin){
    stepsPerRev=SRev;
    stepPin=Spin;
    pinMode(Spin, OUTPUT);
    dirPin=Dpin;
    pinMode(Dpin, OUTPUT);
  }

  SimpleStepper::SimpleStepper(int SRev, int Spin, int Dpin, int newSpeed){
    stepsPerRev=SRev;
    stepPin=Spin;
    dirPin=Dpin;
    stepperSpeed=newSpeed;
    speedSet=true;
    timePerStep=60000/(stepperSpeed * stepsPerRev);
  }

  void SimpleStepper::setSpeed(int newSpeed){
    stepperSpeed = newSpeed;
    speedSet=true;
    timePerStep=60000/(stepperSpeed * stepsPerRev);
  }

  void SimpleStepper::setSteps(int numberOfSteps){
    stepsToMake=abs(numberOfSteps);
    if(numberOfSteps>0){
      dirState=HIGH;
    }
    else{
      dirState=LOW;
    }
    digitalWrite(dirPin, dirState);
  }

  int SimpleStepper::setRevs(float numberOfRevs){
   int nos = round(numberOfRevs*stepsPerRev);
   setSteps(nos);
   return nos;
  }
  
  int SimpleStepper::run(){
    if(speedSet == true){
      if(stepsToMake > 0){
        long currentTime=millis();
        if(stepPinState == LOW){
           if(currentTime>(previousStepTime+(timePerStep/2))){
            stepPinState=HIGH;
            previousStepTime=currentTime; 
          }        
        }
        else{
          if(currentTime>(previousStepTime+(timePerStep/2))){
            stepPinState=LOW;
            previousStepTime=currentTime;
            stepsToMake--; 
          }
        }
      digitalWrite(stepPin, stepPinState);
      }
      else{
        return 2;     //No more steps to make
      }
    return 0;
    }
    return 1;   //speed was not set
  }
