/*
uc_master
Write by: Felipe Hooper
Electronic Engineer
*/

#include <avr/wdt.h>
#include "mlibrary.h"


void setup() {
  wdt_disable();

  Serial.begin(9600);
  mySerial.begin(9600);
  granotec.begin(9600);

  message.reserve(65);

  DDRB = DDRB | (1<<PB0) | (1<<PB5);
  PORTB = (0<<PB0) | (1<<PB5);

  wdt_enable(WDTO_8S);
}


void loop() {
  if ( stringComplete  ) {
      if ( validate() ) {
          PORTB = 1<<PB0;

          switch ( message[0] ) {
              case 'r':  //lectura de sensores
                hamilton_sensors();
                daqmx();
                control_ph();
                control_temp();
                broadcast_setpoint(0);
                break;

              case 'w':  //setpoints
                setpoint();
                control_ph();
                control_temp();
                broadcast_setpoint(1);
                break;

              case 'c':  //calibracion de sensores
                sensor_calibrate();
                break;

              case 'u':  //umbrales actuadores motores
                actuador_umbral();
                break;

              case 'a':  //setpoint electrovalvulas y motor
                uc_granotec('c');
                break;

              default:
                break;
          }

          PORTB = 0<<PB0;
      }
      else {
        Serial.println("bad validate");
      }

    clean_strings();
    wdt_reset();
  }
}
