/*
  Stepper.h - A Simple Library for non blocking stepper motor use with driver board.
  Created by J. Gladines Januari 2019.
  Released into the public domain.
*/
#ifndef SimpleStepper_h
#define SimpleStepper_h

#include "Arduino.h"

class SimpleStepper{
  //public functions and vars
  public:
    
    //variables
    int stepsPerRev; 
    int stepperSpeed;    //rpm
    int stepPin;
    int stepPinState=LOW;
    int dirPin;
    int dirState=HIGH;
    bool speedSet=false;
    
    //constructor(s)
    SimpleStepper(int SRev, int Spin, int Dpin);
    SimpleStepper(int SRev, int Spin, int Dpin, int newSpeed);
  
    void setSpeed(int newSpeed);
    void setSteps(int numberOfSteps);
    int setRevs(float numberOfRevs);
    int run();

  //private functions and vars
  private:
    long previousStepTime=0;
    long timePerStep;
    int stepsToMake;  
};

#endif
