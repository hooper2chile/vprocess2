/*
  uc_granotec, Specific design for IDIN-BIOCL: Granotec Client
  write by: Felipe Hooper
  Electronic Engineer

*/

#include <avr/wdt.h>
#include <slibrary_granotec.h>

void setup() {
  wdt_disable();

  Serial.begin(9600);
  DDRB  = DDRB  | (1<<PB1) | (1<<PB2) | (1<<PB3) | (1<<PB4);  //Pin out setup
  PORTB = PORTB | (1<<PB1) | (1<<PB2) | (1<<PB3) | (1<<PB4);  //pin out low level

  message.reserve(65);
  wdt_enable(WDTO_8S);
}

//Relay with inverter logical
void loop() {
  if ( stringComplete ) {
    switch ( message[0] )
    {
      case 'a': //a-gua
        digitalWrite(v1, LOW);
        digitalWrite(v2, LOW);
        digitalWrite(v3, HIGH);
        digitalWrite(v4, HIGH);
        break;

      case 'v': //v-apor
        digitalWrite(v3, LOW);
        digitalWrite(v4, LOW);
        digitalWrite(v1, HIGH);
        digitalWrite(v2, HIGH);
        break;

      default:
        digitalWrite(v1, HIGH);
        digitalWrite(v2, HIGH);
        digitalWrite(v3, HIGH);
        digitalWrite(v4, HIGH);
        break;
    }

    Serial.print("Se recibio:\t");
    Serial.println(message);

    stringComplete = false;
    message = "";
  }
delay(500);
wdt_reset();

}
