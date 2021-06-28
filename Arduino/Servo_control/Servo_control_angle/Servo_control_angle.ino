/*


*/

#include <Servo.h>
#include <SoftwareSerial.h>   
#include <SerialCommand.h>
#include <AccelStepper.h>

SerialCommand SCmd; 

Servo servo_rot;
Servo servo_tilt;


AccelStepper stepper = AccelStepper(AccelStepper::DRIVER, 4, 7); 

float pitch = 8.00;   
float spr = 200;  
int stepperEnablePin = 8;  
int uddir = 1; 


void setup() {

  setup_servo();

  servo_rot.attach(5);
  //servo_tilt.attach(6);


  
  Serial.begin(9600);
  SCmd.addCommand("R",change_angle_rot);
  SCmd.addCommand("T",change_angle_tilt);
  SCmd.addCommand("Rs",Rotate_step);
  SCmd.addCommand("Ts",Tilt_step);
  SCmd.addCommand("Info",send_info);
  SCmd.addCommand("M",move_stepper);
  SCmd.addDefaultHandler(unrecognized); 

  Serial.println("Camera");   
 
}

void setup_servo(){
  stepper.setMaxSpeed(500);                       
  stepper.setAcceleration(5000);
  pinMode(stepperEnablePin, OUTPUT);                 
  digitalWrite(stepperEnablePin, LOW);  
}

void loop() {
  
SCmd.readSerial();

} 


void send_info(){
  Serial.println("Camera");  
}

void change_angle_rot() 
{
  float angle;  
  char *arg; 

  arg = SCmd.next();                                                                                            
    angle=atof(arg);                                                                                           
      rot_moveTo(angle,25);                               
      Serial.print(" Changing rotation angle to");
      Serial.println(angle);
      delay(10);
  
    }

void change_angle_tilt() 
{
   float angle;  
  char *arg; 

  arg = SCmd.next();                                                                                            
    angle=atof(arg);                                                                                           
      tilt_moveTo(angle,25);                               
      Serial.print(" Changing tilt angle to");
      Serial.println(angle);
      delay(10);
  
    }

void rot_moveTo(int position, int speed) {
  int pos = servo_rot.read();
  int pos1 = pos;
  if(position > pos){
    for (pos=pos1;pos<=position;pos += 1){
      servo_rot.write(pos);
      pos1 = pos;
      delay(speed); 
    }
  } else {
      for (pos = pos1;pos>= position; pos-=1){
      servo_rot.write(pos);
      pos1=pos;
      delay(speed);
    }
   }
  }


void tilt_moveTo(int position, int speed) {
  int pos = servo_tilt.read();
  int pos2=pos;
  if(position > pos){
    for (pos=pos2;pos<=position;pos += 1){
      servo_tilt.write(pos);
      pos2 = pos;
      delay(speed); 
    }
  } else{ 
      for( pos = pos2;pos>= position; pos-=1){
      servo_tilt.write(pos);
      pos2=pos;
      delay(speed);
    }
  }
}
void Rotate_step(){
  float step;  
  char *arg; 

  arg = SCmd.next();                                                                                            
    step=atof(arg);  
   float pos = servo_rot.read();
   int newpos= pos + step;                                                                                         
      rot_moveTo(newpos,25); 
}

void Tilt_step(){
  float step;  
  char *arg; 

  arg = SCmd.next();                                                                                            
    step=atof(arg);  
    int pos = servo_tilt.read();
    int newpos= pos + step;                                                                                         
      tilt_moveTo(newpos,25); 
}
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
