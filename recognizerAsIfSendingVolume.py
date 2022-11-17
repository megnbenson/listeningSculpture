#pip3 install SpeechRecognition 
#pip3 install pyaudio (check if you need other extras, https://github.com/Uberi/speech_recognition )
#pip3 install textblob
#python3 -m textblob.download_corpora
#pip3 install python-osc

import speech_recognition as sr
from textblob import TextBlob
from pythonosc import udp_client
import time
import random


def sendingVol():
    #volume = input("please enter volume")
    for i in range(0,10):
        volume = (i+random.randrange(50))/100
        client.send_message("/mouth/gain",volume)
        time.sleep(1.0)
        print(f"vol: {volume}")
    #client.send_message("/colour", "255,255,255")

    #for i in range(-2, 2):
    #    client.send_message("/volume", i)
     #   time.sleep(1)


if __name__ == "__main__":
    

     # Set OSC stuff
    #ip = "192.168.0.2"
    ip = "192.168.38.74"
    
    port = 6006
    client = udp_client.SimpleUDPClient(ip, port)
    

    listening = True
    
                
    while listening:     
        try: 
            print("Listening to volume...")
            sendingVol()
            print("sent OSC")

        except sr.UnknownValueError:
            print("Not recognized, sending default values...")
            client.send_message("/mouth/gain", 0.6)
            #client.send_message("/colour", "255,255,0")
            print("sent default OSC")