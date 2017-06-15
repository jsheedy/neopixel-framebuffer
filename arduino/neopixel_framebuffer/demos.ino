#include <math.h>

float point1 = 0.0;
float velocity1 = 0.01; //1.0/(float)(NLEDS);

float point2 = 0.0;
float velocity2 = -0.01; //1.0/(float)(NLEDS);

float randKick() {
  return (float)(random(0,1000)-500) / 500 * 0.0001;  
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
  point1 = (point1 + velocity1);  
  point2 = (point2 + velocity2);

  velocity1 += randKick();
  velocity2 += randKick();
  
  if (point1 >= 1.0) {
    point1 = 0.0;
  }
  if (point2 <= 0.0) {
    point2 = 1.0;
  }
  
  float width = 0.025;
  
  for (uint16_t i = 0; i < NLEDS; i++) {
    float iPoint = (float)i / NLEDS;
    float delta1 = deltaPoints(iPoint, point1);
    float delta2 = deltaPoints(iPoint, point2);

    if (delta1 < width && delta2 < width) {
      strip.setPixelColor(i, 255, 0, 0);    
    }
    else if (delta1 < width) {
      int red = (int)(255.0 * (1-(delta1/width)));    
      strip.setPixelColor(i, red, 0, 0 );    
    }
    else if (delta2 < width) {
      int color = (int)(255.0 * (1-(delta2/width)));    
      strip.setPixelColor(i, 0, 0, color);    
    }
    else {
      strip.setPixelColor(i, 0,0,0);    
    }
  }
  strip.show();
}

int red = 1;
int delta = 1;

void demo1() {
   if (red == 255) {
    delta = -1;
  }
  if (red == 0) {
    delta = 1;
  }
  red += delta;
  for (uint16_t i = 0; i < NLEDS; i++) {
    strip.setPixelColor(i, red, (i*red)%255, 255-red );
  }
  strip.show();
}

void colorTest(int colorIndex) {
  rgb[0] = 0;
  rgb[1] = 0;
  rgb[2] = 0;
  rgb[colorIndex] = 255;
  int skip = 5;
  for (uint16_t i = colorIndex; i < NLEDS; i+=skip) {
    strip.setPixelColor(i-skip, 0, 0, 0 );
    strip.setPixelColor(i, rgb[0], rgb[1], rgb[2] );
    strip.show();
  }
}
