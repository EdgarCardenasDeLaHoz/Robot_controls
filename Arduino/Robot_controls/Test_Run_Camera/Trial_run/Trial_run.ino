
#include <SoftwareSerial.h>                         //libraries for the processing of the serial command and to controll the stepper motors
#include <SerialCommand.h>
#include <AccelStepper.h>
#include <Wire.h>
#include <ArduinoJson.h>

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
String info_command = "";

void setup() {
  pinMode(stepperEnablePin, OUTPUT);
  digitalWrite(stepperEnablePin, LOW);

  for (int i = 0; i <= 3; i++) {                    //set the maximum speed and acceleration for the stepper motors
    steppers[i].setMaxSpeed(2500);
    steppers[i].setAcceleration(1000);
  }
  SCmd.addCommand("Start", sequence);
  SCmd.addCommand("M", motor);
  SCmd.addCommand("Home", go_home);
  Wire.begin(8);
  Wire.onReceive(receiveEvent);
  Serial.begin(9600);
  Serial.println("Robotic Arm");
  //
}

void loop() {
  SCmd.readSerial();
  for (int i = 0; i <= 3; i++) {                    //set the maximum speed and acceleration for the stepper motors
    steppers[i].run();
  }

  if (millis() - lastMillis >= 2 * 60 * 1000UL) {
    lastMillis = millis();  //get ready for the next iteration
    check_move_complete();
  }
  if (info_command != ""){
    wire_command();
    delay(100);
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

void receiveEvent(int howMany) {
 while (0 <Wire.available()) {
    char c = Wire.read();   
    info_command += c;
  }
  Serial.println(info_command);
  
}

void wire_command(){
  int Start;
  int amount_X;
  int amount_Y;
  int step_idx;
  int distance_mm;
  
  DynamicJsonBuffer jsonBuffer;
      JsonObject& root= jsonBuffer.parseObject(info_command);
  if (root.success()) {
         Start = atoi(root["Start"]);
         amount_X = atoi(root["x"]);
         amount_Y = atoi(root["y"]);
         step_idx = atoi(root["M"]);
         distance_mm = atoi(root["distance"]);
      }
   if(Start == 1){
    scan(amount_X,amount_Y);
    }
   if(step_idx == 1){
    move_stepper(0,distance_mm);
    }
   if(step_idx == 2){
    move_stepper(1,distance_mm);
    }
    
   Start = 0;
   amount_X = 0;
   amount_Y = 0;
   step_idx = 0;
   distance_mm = 0;
   info_command = "";
  }

void sequence(){
  int amount_X;
  int amount_Y;
  char *arg;
    
  arg = SCmd.next();
  
    if (arg == NULL)   {
      Serial.println("Not recognized: No hieght parameter given");
      return;
    }
    
  amount_X = atof(arg);
    if (amount_X == 0) {
      Serial.println("Not recognized: Height parameter not parsed");
      return;
    }

  arg = SCmd.next();
    if (arg == NULL)   {
      Serial.println("Not recognized: No hieght parameter given");
      return;
    }
  
  amount_Y = atof(arg);
    if (amount_Y == 0) {
      Serial.println("Not recognized: Height parameter not parsed");
      return;
    }

  scan(amount_X,amount_Y);
  
  }
void motor(){
  int idx;
  int distance;
  char *arg;
    
  arg = SCmd.next();
  Serial.println(arg);
  idx = atof(arg);
  
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
  move_stepper(idx,distance);
  }
void scan(int X, int Y){
  
  float distance_X;
  float distance_Y;
 // Serial.println(X);
  //Serial.println(Y);
  //Serial.println("amount of pictures ");
  //Serial.println(X);
 // Serial.println("Degrees moved per picture");
  distance_X = 120 * 32 * 2.778 / (X-1);
 // Serial.println(distance_X);

  //Serial.println(X);
  //Serial.println(Y);
  
  //Serial.println("amount of pictures ");
 // Serial.println(Y);
 // Serial.println("Degrees moved per picture");
  distance_Y = 90 * 32 * 2.778 / (Y-1);

  for (int b=0 ; b < Y ; b=b+1){
     // Serial.println("hallo");
      if  (b % 2 == 0) {
          for (int i=0 ; i < X-1 ; i=i+1){
              steppers[0].move(distance_X);
              while (steppers[0].isRunning() == 1) {
                  steppers[0].run();
              }
              delay(100);
              //Serial.println("Move x positive");
              b_move_complete = false;         
              Serial.println(".");
            }
          }
      if (b % 2 != 0) {
          for (int i=0 ; i < X-1 ; i=i+1){
              steppers[0].move(-distance_X);
              while (steppers[0].isRunning() == 1){
                  steppers[0].run();
              }
              delay(100);
              //Serial.println("Move x negative");
              b_move_complete = false;      
             // Serial.println(".");
            }
          }
        if (b<Y-1) {
            steppers[1].move(distance_Y);
              while (steppers[1].isRunning() == 1) {
                  steppers[1].run();
              }
            delay(100);
           // Serial.println("Move y");
          }
    }
    X = 0;
    Y = 0;
    distance_X = 0;
    distance_Y = 0;
    go_home();
 }

 void go_home(){
  //Serial.println("Going home.");
    steppers[0].moveTo(0);
    steppers[0].runToPosition();
    steppers[1].moveTo(0);
    steppers[1].runToPosition();
  }

void move_stepper(int idx, int distance_mm){
  float distance;
  if (distance_mm == 0) {
    Serial.println("Not recognized: Height parameter not parsed");
    return;
  }
  distance = distance_mm * 32 * 2.778;
  Serial.println("moving");
  Serial.println(distance);
  Serial.println("Degrees");
  Serial.println(idx);
  if (idx == 0) { 
    Serial.println(distance);
    steppers[0].move(distance);
    /*while (steppers[0].isRunning() == 1) {
            steppers[0].run();
    }*/
    Serial.println("M0 knows the distance");
  }
  
  if (idx == 1) {
    Serial.println("moving step 1");
    steppers[1].move(distance);
    /*while (steppers[1].isRunning() == 1) {
            steppers[1].run();
    }*/
    Serial.println("M1 knows the distance");
  }
  }
