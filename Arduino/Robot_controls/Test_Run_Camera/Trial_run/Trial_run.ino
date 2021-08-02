
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

  SCmd.addCommand("Start", move_stepper);
  
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


void move_stepper() {
  float amount_X;
  float distance_X;
  float amount_Y;
  float distance_Y;
  
  char *arg;
  int step_idx;

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

  Serial.print("amount of pictures ");
  Serial.print(amount_X);
  Serial.println(" Degrees moved per picture");

  distance_X = 120 * 32 * 2.778 / (amount_X-1);
  Serial.println(distance_X);

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

  Serial.print("amount of pictures ");
  Serial.print(amount_Y);
  Serial.println(" Degrees moved per picture");

  distance_Y = 90 * 32 * 2.778 / (amount_Y-1);
  Serial.println(distance_Y);
  Serial.println(amount_Y);
  Serial.println(amount_X);
  Serial.println(distance_X);

  for (int b=0 ; b < amount_Y ; b=b+1){
    Serial.println("hallo");
     if  (b % 2 == 0) {
        for (int i=0 ; i < amount_X ; i=i+1){
            steppers[0].move(distance_X);
            delay(10);
            Serial.println("Move x positive");
            b_move_complete = false;
        }
     }
     if (b % 2 != 0) {
        for (int i=0 ; i < amount_X ; i=i+1){
            steppers[0].move(-distance_X);
            delay(10);
            Serial.println("Move x negative");
            b_move_complete = false;
        }
      }
      steppers[1].move(distance_Y);
      delay(10);
      Serial.println("Move y");
     }
  }
