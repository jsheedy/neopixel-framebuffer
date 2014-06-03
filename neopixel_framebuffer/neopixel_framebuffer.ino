#include <Adafruit_NeoPixel.h>

#define PIN 6
#define NLEDS 420

//#define BAUD 115200
//#define BAUD 230400
#define BAUD 460800

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NLEDS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(BAUD);
  strip.begin();
  bassNuke();
  allBlue();
  Serial.println("BOOTED");
}
int d=1;
int ramp(int x) {
  x += d;
  if (x >= 255) {
    d=-1;
  }
  if (x <= 0) {
    d = 1;
  }
  return x;
}

int p=0;
int q=0;

char rgb[3];
int t=0;
void loop() {
    if (Serial.available() > 0) {
      for(uint16_t i=0; i<NLEDS; i++) {
          Serial.readBytes(rgb,3);
        strip.setPixelColor(i,rgb[0],rgb[1],rgb[2]);
      }
      strip.show();
    } 
    else {
     pulse2(); 
    }
}

void bassNuke() {
  strobe();
  delay(50);
  strobe();
  delay(10);
  strobe();
}

void strobe() {
  allWhite();
  delay(10);
  allBlack();
}
void pulse2() {
  int r = 0;
  int g = 0;
  
  int b = q;
  strip.setPixelColor(p, r,g,b);
  strip.show();
  p++;
  if (p>NLEDS){
    p=0;
  }
  if (q > random(0,10000)){
     q=0;
  } else { q++; }
}
void pulse() {
  int r = int(.1*random(0,256));
  int g = int(.1*random(0,256));
  
  for(uint16_t i=0; i<strip.numPixels(); i++) {
    int b = random(0,256);
    strip.setPixelColor(p, r,g,b);
  }
  strip.show();
  p++;
  if (p>NLEDS){
    p=0;
  }
}
void allWhite() {
  for(uint16_t i=0; i<strip.numPixels(); i++) {
      strip.setPixelColor(i, 255,255,255);
  }
  strip.show();
}
void allBlack() {
  for(uint16_t i=0; i<strip.numPixels(); i++) {
      strip.setPixelColor(i, 0, 0, 0);
  }
  strip.show();
}
void allBlue() {
  for(uint16_t i=0; i<strip.numPixels(); i++) {
      strip.setPixelColor(i, 0, 0, 255);
  }
  strip.show();
}
