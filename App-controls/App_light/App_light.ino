#include <BlynkSimpleEsp8266.h> 
#include <Wire.h>

#define RelayPin1 5  //D1

#define VPIN_BUTTON_1    V1
#define VPIN_SLIDE_1   V2 

int toggleState_1 = 0;
int toggleState_2 = 0;
String text = "";
int wifiFlag = 0;

#define AUTH "vpbr94yHUzt59g0Ad2kGt5zCQqzt3Jtg"                 // You should get Auth Token in the Blynk App.  
#define WIFI_SSID "neuai"             //Enter Wifi Name
#define WIFI_PASS "123456789"         //Enter wifi Password

BlynkTimer timer;

BLYNK_CONNECTED() {
//  // Request the latest state from the server
  Blynk.syncVirtual(VPIN_BUTTON_1);
  Blynk.syncVirtual(VPIN_SLIDE_1);
}

BLYNK_WRITE(VPIN_BUTTON_1) {
  toggleState_1 = param.asInt();
  if (toggleState_1 == 1) {
    Wire.beginTransmission(8);
    Wire.write("{\"change\":1,\"gpio\":13,\"state\":1}");
    Wire.endTransmission();
    }
  else if (toggleState_1 == 0) {
    Wire.beginTransmission(8);
    Wire.write("{\"change\":1,\"gpio\":13,\"state\":0}");
    Wire.endTransmission();
    }
}

BLYNK_WRITE(VPIN_SLIDE_1) {
  toggleState_2 = param.asInt();
  Wire.beginTransmission(8);
  text = "{\"change\":2,\"gpio\":5,\"state\":"+String(toggleState_2)+"}";
  Wire.write(text.c_str());
  Wire.endTransmission();
  }

void checkBlynkStatus() { // called every 3 seconds by SimpleTimer

  bool isconnected = Blynk.connected();
  if (isconnected == false) {
    wifiFlag = 1;
  }
  if (isconnected == true) {
    wifiFlag = 0;
    Blynk.virtualWrite(VPIN_BUTTON_1, toggleState_1);
    Blynk.virtualWrite(VPIN_SLIDE_1, toggleState_2);
}
}
void setup()
{
  Serial.begin(9600);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Wire.begin(D1,D2);
  timer.setInterval(3000L, checkBlynkStatus); // check if Blynk server is connected every 3 seconds
  Blynk.config(AUTH);
  delay(1000);
  Blynk.virtualWrite(VPIN_BUTTON_1, toggleState_1);
  Blynk.virtualWrite(VPIN_SLIDE_1, toggleState_2);
}

void loop(){  
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("WiFi Not Connected");
    //digitalWrite(wifiLed, HIGH);
  }
  else
  {
    Serial.println("WiFi Connected");
    //digitalWrite(wifiLed, LOW); //Turn on WiFi LED
    Blynk.run();
  }

  timer.run(); // Initiates SimpleTimer
}
