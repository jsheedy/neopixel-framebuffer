#include <Adafruit_NeoPixel.h>

#define PIN 6
#define NLEDS 420

//#define BAUD 115200
//#define BAUD 230400
#define BAUD 460800

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NLEDS, PIN, NEO_RGB + NEO_KHZ800);
//Adafruit_NeoPixel strip = Adafruit_NeoPixel(NLEDS, PIN, NEO_RGB + NEO_KHZ800);

void setup() {
  Serial.begin(BAUD);
  strip.begin();
  // bleed off mysterious bytes
  while(Serial.available() > 0) {
    Serial.read();
  }
}

byte rgb[3];

void loop() {
  Serial.write(0);
  if (Serial.available() > 0) {
    for (uint16_t i = 0; i < NLEDS; i++) {
      Serial.readBytes(rgb, 3);
      strip.setPixelColor(i, rgb[2], rgb[1], rgb[0]);
    }
    strip.show();
  }
}
