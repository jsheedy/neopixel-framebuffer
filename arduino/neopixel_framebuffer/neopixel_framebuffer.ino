#include <FastLED.h>

#define DATA_PIN 6
#define CLOCK_PIN 6
#define NLEDS 420
#define BAUD 460800
#define SERIAL_TIMEOUT 50  // milliseconds before idle function called

CRGB leds[NLEDS];

byte rgb[3];
int frame = 0;

void idle() {
  for (int i=0; i<40; i++) {
    waves();
  }
}

void bleed() {
  // bleed off xtra bytes
  while(Serial.available() > 0) {
    Serial.read();
  }
}

void setup() {
  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NLEDS);
  FastLED.setBrightness( 100);  
  Serial.setTimeout(SERIAL_TIMEOUT);
  Serial.begin(BAUD);
}

void loop() {
  bleed();
  Serial.write(0); 
  frame = frame+1;
  for (uint16_t i = 0; i < NLEDS; i++) {
    int bytesRead = Serial.readBytes(rgb, 3);
    if (bytesRead == 3) {
      leds[i] = CRGB(rgb[0], rgb[1], rgb[2]);
    } else {
      idle();
      break;
    }
  }
  FastLED.show();
}
