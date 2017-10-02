/*
  * uc_granotec
  Specific design for IDIN-BIOCL: Granotec Client

  write by: Felipe Hooper
  Electronic Engineer
*/

#define v1 12
#define v2 11
#define v3 10
#define v4 9


#include <Arduino.h>

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
