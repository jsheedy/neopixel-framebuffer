#include <Adafruit_NeoPixel.h>

#define PIN 6
#define NLEDS 420

#define BAUD 460800

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NLEDS, PIN, NEO_GRB + NEO_KHZ800);

void colorTest(int colorIndex) {
  byte rgb[3] = {0,0,0};
  rgb[colorIndex] = 255;
  int skip = 5;
  for (uint16_t i = colorIndex; i < NLEDS; i+=skip) {
    strip.setPixelColor(i-skip, 0, 0, 0 );
    strip.setPixelColor(i, rgb[0], rgb[1], rgb[2] );
    strip.show();
  }
}
void setup() {
  strip.begin();

  colorTest(0);
  colorTest(1);
  colorTest(2);

  Serial.begin(BAUD);

  // bleed off mysterious bytes
  while(Serial.available() > 0) {
    Serial.read();
  }
}

byte rgb[3];

void loop() {
  Serial.write(0);
  for (uint16_t i = 0; i < NLEDS; i++) {
    Serial.readBytes(rgb, 3);
    strip.setPixelColor(i, rgb[0], rgb[1], rgb[2]);
  }
  strip.show();
}
