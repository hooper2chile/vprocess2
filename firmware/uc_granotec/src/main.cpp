/*
  uc_granotec,
  Specific design for IDIN-BIOCL: Granotec Client

  writed by: Felipe Hooper
  Electronic Engineer
*/

#include <avr/wdt.h>
#include <slibrary_granotec.h>

void setup() {
  wdt_disable();

  Serial.begin(9600);
  pinMode(PWM_PIN, OUTPUT);
  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);

  DDRB  = DDRB  | (1<<PB1) | (1<<PB2) | (1<<PB3) | (1<<PB4) | (1<<PB0);  //Pin out setup
  PORTB = PORTB | (1<<PB1) | (1<<PB2) | (1<<PB3) | (1<<PB4) | (1<<PB0);  //pin out high level <=> off relay pin

  DDRD  = DDRD  | (1<<PD7) | (1<<PD6);
  PORTD = PORTB | (1<<PD7) | (1<<PD6);

  message.reserve(65);
  setup_default();

  wdt_enable(WDTO_8S);
}

//Relay with inverter logical
void loop() {
  if ( stringComplete ) {
      //wdt_reset();
      switch ( message[0] )
      {
          case 'a': //a-gua
            setup_default();
            bomb();
            hot_water_valve();
            break;

          case 'v': //v-apor
            setup_default();
            bomb();
            steam_valve();
            break;

          case 'm': //m-otor
            motor_set();

            break;

          default:
            setup_default();
            break;
      }
      Serial.print("uc_granotec command update:\t");
      Serial.println(message);

      stringComplete = false;
      message = "";
  }
  //else setup_default();
  wdt_reset();
  delay(500);

}
