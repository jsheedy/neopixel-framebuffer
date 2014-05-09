neopixel-framebuffer
====================

A Python server which defines a linear video buffer which is drawn to a NeoPixel strip driven by an Arduino.  

The package consists of a Python server and Arduino code.

neopixel_framebuffer.py maintains a VideoBuffer object which contains a numpy array representing each of your LED pixels.  A thread 
continuously sends that buffer over USB to the Arduino, which waits for these byte streams.  The baud rate and update frequency can be tuned to achieve maximum performance.   Another thread receives OSC (Open Sound Control) messages.   Those OSC messages can be output from your own code, music control hardware, or apps such as TouchOSC for iOS.

USAGE
-----
./neopixel_framebuffer.py


INSTALLATION
------------
Python3 is required.  
Install the required Python packages into your virtualenv or system with "pip3 install -r requirements.txt".

Configure neopixel_framebuffer/neopixel_framebuffer.ino: set PIN and NLEDS to the output pin your Neopixels are plugged into on your Arduino, and NLEDS is the number of LEDs in your Neopixel strip.   This should be made externally configurable.

Install neopixel-framebuffer.ino on your arduino.

Run ./neopixel_framebuffer.py

Try sending some test messages with test/osc_test_client.py
