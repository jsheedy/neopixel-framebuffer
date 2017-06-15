#include <Adafruit_NeoPixel.h>

#define PIN 6
#define NLEDS 420
#define BAUD 460800
#define SERIAL_TIMEOUT 50  // milliseconds before idle function called

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NLEDS, PIN, NEO_GRB + NEO_KHZ800);
byte rgb[3];
int frame = 0;

void idle() {
  for (int i=0; i<40; i++) {
    waves();
  }
}

void setup() {
  strip.begin();

  colorTest(0);

  Serial.setTimeout(SERIAL_TIMEOUT);
  Serial.begin(BAUD);

  // bleed off mysterious bytes
  while(Serial.available() > 0) {
    Serial.read();
  }
}

int bytesRead = 0;
void loop() {
  Serial.write(0);
  frame = frame+1;
  for (uint16_t i = 0; i < NLEDS; i++) {
    bytesRead = Serial.readBytes(rgb, 3);
    if (bytesRead == 3) {
      strip.setPixelColor(i, rgb[0], rgb[1], rgb[2]);
    } else {
      idle();
    }
  }
  strip.show();
}
