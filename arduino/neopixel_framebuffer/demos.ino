#include <math.h>

float point1 = 0.0;
float velocity1 = 0.005; //1.0/(float)(NLEDS);

float point2 = 0.0;
float velocity2 = -0.005; //1.0/(float)(NLEDS);

float randKick() {
  float kick = (float)(random(0,10000)-5000) / 10000000.0;  
  return kick;
}

float deltaPoints(float p1, float p2) {
  float diff = (p2 - p1);
  if (diff > 0.5) {
    diff -= 1.0;
  }
  if (diff < -0.5) {
    diff += 1.0;
  }
  return fabs(diff);
}

void waves()
{
  float maxVelocity = 0.005;
  velocity1 = constrain(velocity1 + randKick(), -maxVelocity, maxVelocity);
  velocity2 = constrain(velocity2 + randKick(), -maxVelocity, maxVelocity);

  point1 = (point1 + velocity1);  
  point2 = (point2 + velocity2);

  if (point1 >= 1.0) {
    point1 = 0.0;
  }
  if (point1 <= 0.0) {
    point1 = 1.0;
  }
  
  if (point2 >= 1.0) {
    point2 = 0.0;
  }
  if (point2 <= 0.0) {
    point2 = 1.0;
  }  
  float width = 0.025;
  float deltaPoint = deltaPoints(point1, point2);
  int h =  (int)(deltaPoint * 255);
  int s = 255;
    
  for (uint16_t i = 0; i < NLEDS; i++) {
    float iPoint = (float)i / NLEDS;
    float delta1 = deltaPoints(iPoint, point1);
    float delta2 = deltaPoints(iPoint, point2);
    
    if (delta1 < width && delta2 < width) {
      int v = 255;
      leds[i] = CHSV(128,s,v);    
    }
    else if (delta1 < width) {
      int v = (int)(255.0 * (1-(delta1/width))); 
      leds[i] = CHSV(h,s,v);
    }
    else if (delta2 < width) {
      int v = (int)(255.0 * (1-(delta2/width))); 
      leds[i] = CHSV(h+((int)(128*deltaPoint)),s,v);
    }
    else {
      leds[i] = CRGB( 0,0,0);    
    }
  }
  FastLED.show();
}

void demo1() {
  int red = 1;
  int delta = 1;

   if (red == 255) {
    delta = -1;
  }
  if (red == 0) {
    delta = 1;
  }
  red += delta;
  for (uint16_t i = 0; i < NLEDS; i++) {
    leds[i] = CRGB(red, (i*red)%255, 255-red );
  }
  FastLED.show();
}

void colorTest(int colorIndex) {
  rgb[0] = 0;
  rgb[1] = 0;
  rgb[2] = 0;
  rgb[colorIndex] = 255;
  int skip = 5;
  for (uint16_t i = colorIndex; i < NLEDS; i+=skip) {
    leds[i-skip] = CRGB(0, 0, 0 );
    leds[i] = CRGB(rgb[0], rgb[1], rgb[2] );
  }
  FastLED.show();

}
