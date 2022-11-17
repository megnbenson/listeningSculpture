# listeningSculpture
 
 The Ear node for the CHAIN performance at Iklectik, November, 2022
 
 Raspberry pi running LED strip and usb connected microphone, detects speech, depending on keyword lists the LED strip changes from red to blue, with different patterns. Also listening to OSC from other nodes of the performace (e.g. volume) and sending out information to other nodes (e.g. color data and text said)
 
 Run the listener and the lights file from separate terminals in the same raspberry pi. the tutorial used to set up the pi and the LEDs is here:
 https://core-electronics.com.au/guides/ws2812-addressable-leds-raspberry-pi-quickstart-guide/
 
 For the listener you'll need to install the bits at the top of the file (I used sudo pip3 install ...) (if i didn't use sudo, the lights didn't work for some reason)
 For the lights you'll need the rpi-ws281x library: (install in the same way^) https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/examples/strandtest.py

it should work, you'll need the internet for the listener as its using google api speechRecognition

Final thoughts / todo:
- listener worked for the most part but would get stuck on listening... with a lot of ambient noise (our way of dealing with this was to restart it manually, perhaps a quicker rate of restart is needed)
- We had two pis running two different LED strips, which meant any delay from one caused them to go out of sync, not necessarily a bad thing as having two separate listeners and LED strips meant less overall dependency on one pi, however perhaps having just one pi running the Lights and another listening would have made it easier on the computing power? and hence less of a delay? more testing necessary there
- The interaction that was played with most in the performance was mostly people talking into the microphones and having delight to hear the text to speech out loud echoed in the room, or seeing what they'd said on screen and asking if it was a chat bot. The LEDs were nice aesthetically but not super clear on the interaction of colour to words and perhaps not a very satisfying interaction as much as hearing your words being interpreted by an automated voice.
- The volume of the speaker did not reflect in the LED brightness at all.

I think in a new iteration i would want to consider having:
- one pattern of lights that is not 'breathing' and is purely reactive to the volume of the speaker (so is on when they're talking) (or adds blue when talking) (but is clear)
- one pattern of lights that is the startFromMiddle pattern where you can see the colour being added
- the glitch pattern having more variation 
- more thought around specific commands to give and what that would repeat (perhaps some added chatbot like aspect, perhaps certain patterns that only occur with one particular phrase) (although that veers towards a tackier feel e.g. a fire pattern lol or a rainbow, so caution required)
