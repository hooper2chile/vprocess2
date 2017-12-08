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

  //POWER ON INDICATOR
  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);
  //************************

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
      switch ( message[0] )
      {
          case 'a': //a-gua fria (enfria con agua de la llave)
            setup_default();
            hot_water_valve();
            break;

          case 'v': //v-apor (calentar en realidad)
            setup_default();
            bomb();
            steam_valve();
            break;

          case 'm': //m-otor
            motor_message();
            break;

          case 'd':
            setup_default();
            break;
      }
      //Serial.print("uc_granotec command update:\t");
      Serial.println(message);

      stringComplete = false;
      message = "";
  }
  motor_set();
  wdt_reset();
  delay(250);
}
