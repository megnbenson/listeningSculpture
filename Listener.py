#!/usr/bin/env python3
#pip3 install SpeechRecognition
#pip3 install pyaudio (check if you need other extras, https://github.com/Uberi/speech_recognition )
#pip3 install textblob
#python3 -m textblob.download_corpora

# sys is part of python and accesses the os
import sys
import speech_recognition as sr
from textblob import TextBlob
#sending osc (client)
from pythonosc import udp_client
import schedule
import os
import sys

# Gathers the keywords to so that the lights operate in a queue.
# Enormously important as without this, the lights functions
# will overlap on the executing leds (which is kinda cool) and will
# eventually overload the strip.
keywords = []

listening = True
mic = sr.Microphone()
rec = sr.Recognizer()

#eye takes the color
clientIp = "10.0.0.158"
#LED / MY IP
#ledIp = "192.168.38.74"
ledIp = "10.0.0.11"
#hub takes all the info
#hubIp = "192.168.0.57"
hubIp = "10.0.0.38"
#hazel is getting string of response for text to speech
#hazelIp ="192.168.65"
hazelIp ="10.0.0.168"

#sending to the eye
senderPort = 6666
#sending to LED
ledSenderPort = 6006
#sending to the hub
hubPort = 9999
hazelPort = 2222

client = udp_client.SimpleUDPClient(clientIp, senderPort)
clientLED = udp_client.SimpleUDPClient(ledIp, ledSenderPort)
clientHub = udp_client.SimpleUDPClient(hubIp, hubPort)
clientHazel = udp_client.SimpleUDPClient(hazelIp, hazelPort)
rgbList = ["100","0","100"]

def restart():
    try:
        print("restart")
        os.system("sudo python3 Listener.py")
    except:
        print("restart exception caught")


def clamp(num, min_value, max_value):
        num = max(min(num, max_value), min_value)
        return num

def interpret(input):
    keywords.clear()
    text = input
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    #check for keywords
    work_words = ["people","because","you","difficult","torture","angry","mean","hard","work","dark","law","project","lived", "job","buy","sell","included", "not enough","affordable","but","system", "shift", "process", "impose""labour", "active", "online", "browse", "loud", "noisy", "print", "send", "receive","faster","harder","more","go","laptop", "computer", "code", "program", "script", "mac", "windows", "microphone", "cable", "light", "screen", "input", "output", "sensor","like", "love", "hate", "think", "I believe", "I want", "I feel"]
    rest_words = ["eventually","later","people","me","help","friendly","nice","easy","simple","land","stop","light","died","compromise","honestly","hopeful","why","what","when","who","listen","friends","neighbour","family","community","release","idyllic","protect","dream","rest", "sleep", "peaceful", "chill", "offline", "off", "closed", "calm", "quiet", "shut", "doze","snooze","tired","sleepy","bed","lazy","nap","peaceful","serene", "take care", "care","please"]
    glitch_words = ["objection","try harder","try","brighter","glitch","stress","strain","broken"]



    # Necessary to define exactly where the file is on the computer.
    lights_path = str(sys.path[0]) + "/Lights.py"

    # This loop will need to be changed as the way it is written
    # means the lights for 'work' will always run first if
    # present. Hasn't been my priority because it does
    # what I need for testing purposes.
    r = int(rgbList[0])
    g = int(rgbList[1])
    b = int(rgbList[2])
    #print(f"rgb: {r},{g},{b}")
    if any(word in text for word in work_words):
        #print(f"count work words: {text.count(word)}")
        work_result = True
        r -= 50
        b += 50
        g =0
        r = clamp(r,0,255)
        g = clamp(g,0,255)
        b = clamp(b,0,255)
        rgbList[0] = r
        rgbList[1] = g
        rgbList[2] = b

        print(f"-> work detected, adding some blue, {str(r)},{str(g)},{str(b)}")
        keywords.append(f"{str(r)},{str(g)},{str(b)}")
    else:
        work_result = False

    if any(word in text for word in rest_words):
        rest_result = True
        g -= 0
        b -=50
        r +=50
        r = clamp(r,0,255)
        g = clamp(g,0,255)
        b = clamp(b,0,255)
        rgbList[1] = g
        rgbList[0] = r
        rgbList[2] = b
        print(f"-> rest detected, adding some red, {str(r)},{str(g)},{str(b)}")
        keywords.append(f"{str(r)},{str(g)},{str(b)}")
    else:
        rest_result = False

    if any(word in text for word in glitch_words):
        glitch_result = True
        keywords.append("glitch")
        print("-> glitch found <-")
    else:
        glitch_result = False

    if work_result==0 and rest_result ==0 and glitch_result==0:  
        if(sentiment > 0.0):
            r += 15
            r = clamp(r,0,255)
            rgbList[0] = r
        else:
            b += 15
            b = clamp(b,0,255)
            rgbList[2] = b
        print(f"-> detected {sentiment} sentiment: {r},{g},{b} sent")
        keywords.append(f"{str(r)},{str(g)},{str(b)}")

# Important and sensitive for-loop
    # This loops through the keywords and opens
    # a parallel instance of lights.py in the background
    # for each keyword. It then passes an input
    # of 'word' to the background process.
    # wait() forces that process to wait for EOF, then
    # close before the next iteration of the loop.

    for color in keywords:
          client.send_message("/ear/color", color)
          clientHub.send_message("/ear/color", color)
          clientLED.send_message("/ear/color", color)
          #print(f"color sent: {color}")

    return sentiment, work_result, rest_result, glitch_result



    """Example main loop that only runs for 10 iterations before finishing"""
with mic as source:
    rec.adjust_for_ambient_noise(source, duration = 1.0)
    rec.dynamic_energy_threshold = True
    rec.pause_threshold = 0.5 #min length of silence
    #rec.energy_threshold = 1200 #400 and 600 ok higher for noisier, under this is considered silent
    try:
        schedule.every(5).minutes.do(restart)
    except sr.UnknownValueError:
        print("Not recognized, stay back wait closer...")

    while listening:
        try:
            schedule.run_pending()
            print(" ")
            print("Listening...")
            audio = rec.listen(source)
            response = rec.recognize_google(audio)
            #response = rec.recognize_sphinx(audio)
            print(response)
            clientHazel.send_message("/ear/response",response)
            sentiment_value, work_words, rest_words, glitch_words = interpret(response) # send to interpret function
            keywords.clear()

        except sr.UnknownValueError:
            print("Not recognized, come closer...")
            #defaultInterpret(0)

