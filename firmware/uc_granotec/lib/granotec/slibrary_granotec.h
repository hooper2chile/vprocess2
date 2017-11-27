/*
  uc_granotec,
  Specific design for IDIN-BIOCL: Granotec Client

  writed by: Felipe Hooper
  Electronic Engineer
*/

#include <Arduino.h>

//Electrovalvula AGUA
#define v1 12
#define v2 11

//Electrovalvula VAPOR
#define v3 10
#define v4 9

//Bomba de agua Trifasica
#define Bomba1   8
#define Bomba2   7

#define PWM_PIN    3
#define VDF_ENABLE 6

String message = "";
boolean stringComplete = false;


void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    message += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

void bomb() {
  digitalWrite(Bomba1, LOW);  //bomba on
  digitalWrite(Bomba2, LOW);  //bomba on
}

void hot_water_valve() {
  digitalWrite(v1, LOW);   //valve hot water on
  digitalWrite(v2, LOW);   //valve hot water on
}

void steam_valve() {
  digitalWrite(v3, LOW); //valve steam on
  digitalWrite(v4, LOW); //valve steam on
}

// default setup:  ALL OFF (HIGH => OFF)
void setup_default() {
  digitalWrite(v1, HIGH);  //valve hot water on
  digitalWrite(v2, HIGH);  //valve hot water on

  digitalWrite(v3, HIGH);  //valve steam off
  digitalWrite(v4, HIGH);  //valve steam off

  digitalWrite(Bomba1, HIGH);  //bomba off
  digitalWrite(Bomba2, HIGH);  //bomba off

  digitalWrite(VDF_ENABLE, HIGH);  //VDF OFF
}

void motor_set() {

  uint16_t rpm_set =  message.substring(1).toFloat();

  Serial.print("message[1:end]:\t");
  Serial.println(message.substring(1).length());

  uint16_t pwm_set = map(rpm_set, 0, 750, 0, 255);

  digitalWrite(VDF_ENABLE, LOW);  //VDF ON
  analogWrite(PWM_PIN, pwm_set);
}
