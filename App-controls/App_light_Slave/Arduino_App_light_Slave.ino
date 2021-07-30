#include <Wire.h>
#include <ArduinoJson.h>

void setup() {
  Wire.begin(8);
  Wire.onReceive(receiveEvent);
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  pinMode(5, OUTPUT);
}

void loop() {
 delay(100);        
}

void processCall(String command){
     DynamicJsonBuffer jsonBuffer;
     JsonObject& root= jsonBuffer.parseObject(command);
     
     if (root.success()) {
         int change = atoi(root["change"]); ## 1 ,2 
         Serial.println(change);
         int gpio = atoi(root["gpio"]); ## 5, 3
         Serial.println(gpio);
         int state = atoi(root["state"]); ## 0 255
         Serial.println(state);

         //set GPIO state
         if (change == 1){ 
          digitalWrite(gpio, state);
         }
         else if (change == 2){
          analogWrite(gpio,state);
         }
       }
  }

void receiveEvent(int howMany) {
  String data="";
 while (0 <Wire.available()) {
    char c = Wire.read();   
    data += c;
    
  }
    Serial.println(data);      
    processCall(data);       
}
