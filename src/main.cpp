#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <PID_v1.h>
#include <math.h>
#include "order.h"
#include "slave.h"


const unsigned char logo [576] PROGMEM = {
	// 'pngegg, 66x64px
	0x00, 0x00, 0x00, 0x01, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3d, 0xef, 0x00, 0x00, 
	0x00, 0x00, 0x00, 0x00, 0x01, 0xfd, 0xef, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0xfd, 0xef, 
	0xf8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfd, 0xef, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1f, 
	0xfd, 0xef, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f, 0xfd, 0xef, 0xff, 0x00, 0x00, 0x00, 0x00, 
	0x00, 0x7f, 0xfd, 0xef, 0xff, 0x80, 0x00, 0x00, 0x00, 0x00, 0x7f, 0xfd, 0xef, 0xff, 0x80, 0x00, 
	0x00, 0x00, 0x00, 0xff, 0xfd, 0xef, 0xff, 0xc0, 0x00, 0x00, 0x00, 0x00, 0xff, 0xfd, 0xef, 0xff, 
	0xc0, 0x00, 0x00, 0x00, 0x01, 0xff, 0xfd, 0xef, 0xff, 0xc0, 0x00, 0x00, 0x00, 0x01, 0xff, 0xfd, 
	0xef, 0xff, 0xe0, 0x00, 0x00, 0x00, 0x01, 0xff, 0xfd, 0xef, 0xff, 0xe0, 0x00, 0x00, 0x00, 0x01, 
	0xff, 0xfd, 0xef, 0xff, 0xe0, 0x00, 0x00, 0x00, 0x01, 0xff, 0xfd, 0xef, 0xff, 0xe0, 0x00, 0x00, 
	0x00, 0x03, 0xff, 0xfd, 0xef, 0xff, 0xf0, 0x00, 0x00, 0x00, 0x03, 0xff, 0xfd, 0xef, 0xff, 0xf0, 
	0x00, 0x00, 0x00, 0x03, 0xff, 0xfd, 0xef, 0xff, 0xf0, 0x00, 0x00, 0x00, 0x03, 0xff, 0xfd, 0xff, 
	0xff, 0xf0, 0x00, 0x00, 0x00, 0x03, 0xff, 0xff, 0xff, 0xff, 0xf0, 0x00, 0x00, 0x00, 0x03, 0xff, 
	0xff, 0xff, 0xff, 0xf0, 0x00, 0x00, 0x00, 0x03, 0xff, 0xff, 0xff, 0xff, 0xf0, 0x00, 0x00, 0x00, 
	0x03, 0xff, 0xff, 0xff, 0xff, 0xf0, 0x00, 0x00, 0x00, 0x07, 0xff, 0xff, 0xff, 0xff, 0xf8, 0x00, 
	0x00, 0x00, 0x07, 0xff, 0xff, 0xff, 0xff, 0xf8, 0x00, 0x00, 0x00, 0x07, 0xf8, 0x7f, 0xff, 0x87, 
	0xf8, 0x00, 0x00, 0x00, 0x0f, 0xdf, 0xdf, 0xfe, 0xfe, 0xfc, 0x00, 0x00, 0x00, 0x0f, 0x7f, 0xff, 
	0xff, 0xff, 0xbc, 0x00, 0x00, 0x00, 0x1f, 0xff, 0xff, 0xff, 0xff, 0xfe, 0x00, 0x00, 0x00, 0x3f, 
	0xe0, 0xff, 0xff, 0xc1, 0xff, 0x00, 0x00, 0x00, 0x3f, 0xb8, 0x3f, 0xff, 0x07, 0x7f, 0x00, 0x00, 
	0x00, 0x7f, 0x70, 0x1f, 0xfe, 0x03, 0xbf, 0x80, 0x00, 0x00, 0xfe, 0xe0, 0x0f, 0xfc, 0x01, 0xdf, 
	0xc0, 0x00, 0x00, 0xfd, 0xe0, 0x07, 0xf8, 0x01, 0xef, 0xc0, 0x00, 0x01, 0xfb, 0xe0, 0x03, 0xf0, 
	0x01, 0xf7, 0xe0, 0x00, 0x03, 0xff, 0xf8, 0x05, 0xe8, 0x07, 0xff, 0xf0, 0x00, 0x03, 0xf7, 0xff, 
	0x07, 0x38, 0x3f, 0xfb, 0xf0, 0x00, 0x07, 0xef, 0xef, 0xff, 0xff, 0xff, 0xfd, 0xf8, 0x00, 0x07, 
	0xef, 0xf3, 0xfe, 0x1f, 0xf3, 0xfd, 0xf8, 0x00, 0x0f, 0xdf, 0xfc, 0x1f, 0x3e, 0x0f, 0xfe, 0xfc, 
	0x00, 0x0f, 0xdf, 0xff, 0xff, 0xff, 0xff, 0xfe, 0xfc, 0x00, 0x1f, 0xdf, 0xff, 0xff, 0xff, 0xff, 
	0xfe, 0xfe, 0x00, 0x1f, 0xbf, 0xf9, 0xe7, 0xf9, 0xe7, 0xff, 0x7e, 0x00, 0x3f, 0xbf, 0xff, 0xef, 
	0xfd, 0xff, 0xff, 0x7f, 0x00, 0x3f, 0x7f, 0xff, 0xbf, 0x3f, 0x7f, 0xff, 0xbf, 0x00, 0x3f, 0x7f, 
	0xff, 0xfe, 0x1f, 0xff, 0xff, 0xbf, 0x00, 0x7f, 0x7f, 0xff, 0x7e, 0x1f, 0xbf, 0xff, 0xbf, 0x80, 
	0x7e, 0xff, 0xff, 0xfe, 0x1f, 0xff, 0xff, 0xdf, 0x80, 0x7e, 0xff, 0xfe, 0xfc, 0xcf, 0xdf, 0xff, 
	0xdf, 0x80, 0xfe, 0xff, 0xee, 0xfa, 0xd7, 0xdd, 0xff, 0xdf, 0xc0, 0xfd, 0xff, 0xff, 0xf6, 0xdb, 
	0xff, 0xff, 0xef, 0xc0, 0x7d, 0xff, 0xf7, 0xe6, 0xd9, 0xfb, 0xff, 0xef, 0x80, 0x7d, 0xf8, 0x17, 
	0xd6, 0xda, 0xfa, 0x07, 0xef, 0x80, 0x3d, 0x80, 0x17, 0xb6, 0xdb, 0x7a, 0x00, 0x6f, 0x00, 0x1c, 
	0x00, 0x1b, 0x36, 0xdb, 0x36, 0x00, 0x0e, 0x00, 0x08, 0x00, 0x0a, 0x36, 0xdb, 0x14, 0x00, 0x04, 
	0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xc0, 
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f, 
	0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
	0x00, 0x03, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x00, 0x00, 0x00, 0x00
};

// SPDX-FileCopyrightText: 2011 Limor Fried/ladyada for Adafruit Industries
//
// SPDX-License-Identifier: MIT

// Thermistor Example #3 from the Adafruit Learning System guide on Thermistors 
// https://learn.adafruit.com/thermistor/overview by Limor Fried, Adafruit Industries
// MIT License - please keep attribution and consider buying parts from Adafruit

// which analog pin to connect
#define THERMISTORPIN A0
// Pin for top of bridge in order to set it high only when measuring
#define TOPBRIDGE 13         
// resistance at 25 degrees C
#define THERMISTORNOMINAL 10000      
// temp. for nominal resistance (almost always 25 C)
#define TEMPERATURENOMINAL 25   
// how many samples to take and average, more takes longer
// but is more 'smooth'
#define NUMSAMPLES 5
// The beta coefficient of the thermistor (usually 3000-4000)
#define BCOEFFICIENT 3040
// the value of the 'other' resistor
#define SERIESRESISTOR 10000
#define COEFA -0.0005832612868399646
#define COEFB 0.0004757002048313418
#define COEFC -5.705419094644155e-07

// For BME280 sensor, Sea level pressure at your location (used for determinng approx altitude)
#define SEALEVELPRESSURE_HPA (1013.25)
//#define SEALEVELPRESSURE_HPA (1029.00)
#define BMP280_ADDRESS 0x76
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// correction de température pour le capteur BME à l'intérieur du boitier
#define deltaTemp 2
#define setOffset 3

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

int samples[NUMSAMPLES];
Adafruit_BME280 bme; // I2C
float humidite, temperature, alpha, rosee, pression, altitude;

//Define Variables we'll be connecting PID to
double Setpoint, Input, Output;
// PWM Pin
#define PIN_OUTPUT 11
//Specify the links and initial tuning parameters
double Kp=80, Ki=2, Kd=5;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

bool is_connected = false; ///< True if the connection with the master is available
uint8_t delta_temp = deltaTemp;
uint8_t set_offset = setOffset;
bool is_full = false;

float steinhart = 0.0f;

float steinhart_hart (float Resistance) {
  float temp;
  
  temp = (1 / (COEFA + (COEFB * log(Resistance)) + (COEFC * pow((log(Resistance)),3) ))) - 273.15;

  return temp;
}

void update_delta_temp(uint8_t delta)
{

  delta_temp = delta - 0x30;
//  Serial.println(delta_temp);
}

void update_setpoint_offset(uint8_t offset)
{
  set_offset = offset - 0x30;
//  Serial.println(set_offset);
}

void full()
{
  is_full = true;
}

void regul()
{
  is_full = false;
}

uint8_t read_i8()
{
	wait_for_bytes(1, 100); // Wait for 1 byte with a timeout of 100 ms
  return (uint8_t) Serial.read();
}

void write_order(enum Order myOrder)
{
	uint8_t* Order = (uint8_t*) &myOrder;
  Serial.write(Order, sizeof(uint8_t));
}


void get_messages_from_serial()
{
  char szF1[8] = "";
  char szF2[8] = "";
  char szF3[8] = "";
  char szF4[8] = "";
  char szF5[8] = "";
  char szF6[8] = "";
  char szF7[8] = "";
  if(Serial.available() > 0)
  {
    // The first byte received is the instruction
    Order order_received = read_order();
    if(DEBUG_PROTO)
    {
      Serial.print("order_received:");
      Serial.print(order_received);
      Serial.println("-");
    }

    if(order_received == HELLO)
    {
      // If the cards haven't say hello, check the connection
      if(!is_connected)
      {
        is_connected = true;
        write_order(HELLO);
      }
      else
      {
        // If we are already connected do not send "hello" to avoid infinite loop
        write_order(ALREADY_CONNECTED);
      }
    }
    else if(order_received == ALREADY_CONNECTED)
    {
      is_connected = true;
    }
    else
    {
      switch(order_received)
      {
        case FULL:
        {
          full();
          if(DEBUG_PROTO)
          {
//            Serial.println("FULL");
            write_order(FULL);
          }
         break;
        }
        case REGUL:
        {
          regul();
          if(DEBUG_PROTO)
          {
//            Serial.println("REGUL");
            write_order(REGUL);
          }
          break;
        }
        case DELTA:
        {
          // between 0 and 20
          update_delta_temp(read_i8());
          if(DEBUG_PROTO)
          {
//            Serial.println("DELTA");
            write_order(DELTA);
          }
          break;
        }
        case OFFSET:
        {
          // between 0 and 20
          update_setpoint_offset(read_i8());
          if(DEBUG_PROTO)
          {
//            Serial.println("OFFSET");
            write_order(OFFSET);
          }
          break;
        }
        case STATUS:
        {
          if(DEBUG_PROTO)
          {
//            Serial.println("STATUS");
            write_order(STATUS);
          }
          dtostrf( temperature, -2, 2, szF1 );
          dtostrf( humidite, -2, 2, szF2 );
          dtostrf( steinhart, -2, 2, szF3 );
          dtostrf( rosee, -2, 2, szF4 );
          dtostrf( Output, -2, 2, szF5 );
          itoa(delta_temp, szF6, 10);
          itoa(set_offset, szF7, 10);
          //snprintf(buf1, 50, "TE:%s-HE:%s-TT:%s-TR:%s-PWM:%s", szF1, szF2, szF3, szF4, szF5);
          Serial.write("[",1);
          Serial.write(szF1,strlen(szF1));
          Serial.write("#",1);
          Serial.write(szF2,strlen(szF2));
          Serial.write("#",1);
          Serial.write(szF3,strlen(szF3));
          Serial.write("#",1);
          Serial.write(szF4,strlen(szF4));
          Serial.write("#",1);
          Serial.write(szF5,strlen(szF5));
          Serial.write("#",1);
          Serial.write(szF6,strlen(szF6));
          Serial.write("#",1);
          Serial.write(szF7,strlen(szF7));
          Serial.write("]",1);

          //printValues(0);
          break;
        }
  			// Unknown order
  			default:
//          Serial.println("ERROR");
          write_order(ERROR);
  				return;
      }
    }
//      Serial.println("RECEIVED");
    write_order(RECEIVED); // Confirm the reception
  }
}


Order read_order()
{
	return (Order) Serial.read();
}

void wait_for_bytes(int num_bytes, unsigned long timeout)
{
	unsigned long startTime = millis();
	//Wait for incoming bytes or exit if timeout
	while ((Serial.available() < num_bytes) && (millis() - startTime < timeout)){}
}

void readValues() {
  temperature = bme.readTemperature();
  temperature = temperature - delta_temp;
  pression = (bme.readPressure() / 100.0F);
  altitude = bme.readAltitude(SEALEVELPRESSURE_HPA);
  humidite = bme.readHumidity();
  
  // calcul du point de rosée (formule de Gustav Magnus-Tetens)
  alpha = log(humidite / 100) + (17.27 * temperature) / (237.3 + temperature);
  rosee = (237.3 * alpha) / (17.27 - alpha);

}

void printValues(float steinhart) {
  if (DEBUG)  {
    Serial.print(F("Température = "));
    Serial.print(temperature);
    Serial.println(" *C");
    
    // Convert temperature to Fahrenheit
    Serial.print(F("Température = "));
    Serial.print(1.8 * temperature + 32);
    Serial.println(" *F");
    
    Serial.print(F("Pression Atm = "));
    Serial.print(pression);
    Serial.println(" hPa");
    
    Serial.print(F("Altitude Approx. = "));
    Serial.print(altitude);
    Serial.println(" m");
    
    Serial.print(F("Humidité = "));
    Serial.print(humidite);
    Serial.println(" %");

    Serial.print(F("Point de rosée = "));
    Serial.print(rosee);
    Serial.println(" *C");

    Serial.println();
  }

  display.clearDisplay();
  display.setTextSize(1);      // Normal 1:1 pixel scale
  display.setTextColor(WHITE); // Draw white text
  display.cp437(true);         // Use full 256 char 'Code Page 437' font
  display.setCursor(0, 0);     // Start at top-left corner
  char buf[32];
  char szF[6];
  dtostrf( temperature, 2, 2, szF );
  sprintf(buf, "Temp Ext : %s C", szF);
  display.println(buf);
  display.setCursor(0, 12);     // Start at top-left corner
  dtostrf( humidite, 2, 2, szF );
  sprintf(buf, "Humidite : %s %%", szF);
  display.println(buf);
  display.setCursor(0, 24);     // Start at top-left corner
  dtostrf( rosee, 2, 2, szF );
  sprintf(buf, "Temp rose : %s C", szF);
  display.println(buf);
  display.setCursor(0, 36);     // Start at top-left corner
  dtostrf( steinhart, 2, 2, szF );
  sprintf(buf, "Temp Tube : %s C", szF);
  display.println(buf);
  display.setCursor(0, 48);     // Start at top-left corner
  dtostrf( Output, 2, 2, szF );
  sprintf(buf, "PWM : %s ", szF);
  display.println(buf);
 
  display.display();
  delay(200);
}

void setup(void) {
  bool status;
  Serial.begin(9600);
  analogReference(EXTERNAL);
  pinMode(TOPBRIDGE, OUTPUT);    // sets the digital pin 13 as output
  digitalWrite(TOPBRIDGE, LOW);
   
  if (DEBUG)  {
    Serial.println(F("Avant Init BME280"));
  }

  status = bme.begin(BMP280_ADDRESS); 
  if (!status) {
    if (DEBUG)  {
      Serial.println(F("Could not find a valid BME280 sensor, check wiring!"));
    }
    while (1);
  }
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    if (DEBUG)  {
      Serial.println(F("SSD1306 allocation failed"));
    }
    //for(;;); // Don't proceed, loop forever
  }

  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
  display.clearDisplay();
  display.drawBitmap(31, 0, logo, 66, 64, WHITE);
  display.display();
  delay(4000); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();
  display.setTextSize(1);      // Normal 1:1 pixel scale
  display.setTextColor(WHITE); // Draw white text
  display.setCursor(0, 0);     // Start at top-left corner
  display.cp437(true);         // Use full 256 char 'Code Page 437' font

  display.println(F("Mesure en cours"));
  display.display();

  //initialize the variables we're linked to
  Input = 40;
  Setpoint = 27;

  //turn the PID on
  myPID.SetMode(AUTOMATIC);

  pinMode(PIN_OUTPUT, OUTPUT);

  delay(2000);

}

void loop(void) {
  uint8_t i;
  float average;

  get_messages_from_serial();

  // take N samples in a row, with a slight delay
  digitalWrite(TOPBRIDGE, HIGH); // set top of the resistor bridge to High
  for (i=0; i< NUMSAMPLES; i++) {
   samples[i] = analogRead(THERMISTORPIN);
   delay(10);
  }
  digitalWrite(TOPBRIDGE, LOW); // set top of the resistor bridge to low in order not to heat the thermistor

  // average all the samples out
  average = 0;
  for (i=0; i< NUMSAMPLES; i++) {
     average += samples[i];
  }
  average /= NUMSAMPLES;

  if (DEBUG)  {
    Serial.print(F("Average analog reading ")); 
    Serial.println(average);
  }
  
  // convert the value to resistance
  average = 1023 / average - 1;
  average = SERIESRESISTOR / average;
  if (DEBUG)  {
    Serial.println(F("* Thermistor resistance *")); 
    Serial.println(average);
  }

/*
  steinhart = average / THERMISTORNOMINAL;     // (R/Ro)
  steinhart = log(steinhart);                  // ln(R/Ro)
  steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
  steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15); // + (1/To)
  steinhart = 1.0 / steinhart;                 // Invert
  steinhart -= 273.15;                         // convert absolute temp to C
  
  Serial.print(F("Temperature : ")); 
  Serial.print(steinhart);
  Serial.println(" *C");
*/
  steinhart = steinhart_hart(average);
  if (DEBUG)  {
    Serial.print(F("Temperature : ")); 
    Serial.print(steinhart);
    Serial.println(" *C");

    Serial.println(F("* Mesures BME280 *"));
  } 
  readValues();
  Input = steinhart;
  Setpoint = max(rosee + set_offset, temperature);
  if (is_full) {
    Output = 255;
    analogWrite(PIN_OUTPUT, Output);
  } else {
    myPID.Compute();
    analogWrite(PIN_OUTPUT, Output);
  }  


  printValues(steinhart);
  delay(3000);
}
