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
  digitalWrite(Bomba1, LOW);  //Contactor bomba on
  digitalWrite(Bomba2, LOW);  //Contactor bomba on
}

void hot_water_valve() {
  digitalWrite(v1, LOW);   //Contactor valve hot water on
  digitalWrite(v2, LOW);   //Contactor valve hot water on
}

void steam_valve() {
  digitalWrite(v3, LOW); //Contactor valve steam on
  digitalWrite(v4, LOW); //Contactor valve steam on
}

// default setup:  ALL Contactor OFF (HIGH => OFF)
void setup_default() {
  digitalWrite(v1, HIGH);  //Contactor valve hot water on
  digitalWrite(v2, HIGH);  //Contactor valve hot water on

  digitalWrite(v3, HIGH);  //Contactor valve steam off
  digitalWrite(v4, HIGH);  //Contactor valve steam off

  digitalWrite(Bomba1, HIGH);  //Contactor bomba off
  digitalWrite(Bomba2, HIGH);  //Contactor bomba off

  digitalWrite(VDF_ENABLE, HIGH);  //VDF OFF
}

uint16_t rpm_set = 0;
void motor_set(char option) {
  //extraction of speed for vdf/motor
  if ( option == 0 ) {
    //Example: message = m0750
    rpm_set =  message.substring(2).toFloat();

    Serial.print("message[1:end]:\t");
    Serial.println(message.substring(1).length());
  }

  else if ( option == 1 ) {
    if ( message[1] == 0 ) {
      uint16_t pwm_set = map(rpm_set, 0, 750, 0, 255);
      digitalWrite(VDF_ENABLE, LOW);  //VDF ON
      analogWrite(PWM_PIN, pwm_set);
    }
    else {
      digitalWrite(VDF_ENABLE, HIGH); //VDF OFF
    }
  }
}
