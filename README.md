﻿# listeningSculpture
 
 The Ear node for the CHAIN performance at Iklectik, November, 2022
 
 Raspberry pi running LED strip and usb connected microphone, detects speech, depending on keyword lists the LED strip changes from red to blue, with different patterns. Also listening to OSC from other nodes of the performace (e.g. volume) and sending out information to other nodes (e.g. color data and text said)
 
 Run the listener and the lights file from separate terminals in the same raspberry pi. the tutorial used to set up the pi and the LEDs is here:
 https://core-electronics.com.au/guides/ws2812-addressable-leds-raspberry-pi-quickstart-guide/
 
 For the listener you'll need to install the bits at the top of the file (I used sudo pip3 install ...) (if i didn't use sudo, the lights didn't work for some reason)
 For the lights you'll need the rpi-ws281x library: (install in the same way^) https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/examples/strandtest.py

it should work, you'll need the internet for the listener as its using google api speechRecognition
