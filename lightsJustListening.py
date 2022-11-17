#receiver:
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio

import time
from rpi_ws281x import PixelStrip, Color

import random
from random import sample


LED_COUNT = 300        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

#ip = "127.0.0.1"
#ip = "192.168.38.74"
ip = "10.0.0.11"
receiverPort = 6006

#to have a global variable of volume it has to be in a dictionary for some reason
lastVol = {'volume':0}
dicVol = {'volume':255, 'step':1}
lastColor = [50,0,0]
currentColor = [218,0,218]
listCol = [currentColor]


def filter_handler(address, *args):
    #print(f"hello volume hello: {args[0]}")
    if  (dicVol['volume'] != int(clamp((float(args[0])*255),10,255))):
        #if vol data is 0-1
        dicVol['volume'] = int(clamp((float(args[0])*255),10,255))
        #dicVol['volume'] = int(clamp(args[0],0,255))
        #print(f"new volume added: {dicVol['volume']}")
        
        dicVol['step'] = int(clamp(float(args[0])*4,1,4))
    
    

dispatcher = Dispatcher()
#volume :
dispatcher.map("/mouth/gain", filter_handler)
#print(dicVol['volume'])

glitchDic = {'isGlitchSwitchOn':0, 'patternNum':0}


def filter_handler_color(address, *args):
    #print(F"hello? : {args[0]}")
    if args[0] == "glitch":
        glitchDic['isGlitchSwitchOn']=1
        print("glitch received")
        glitchDic['patternNum']+=1
        if glitchDic['patternNum'] ==2:
            glitchDic['patternNum']=0
        print(f"pattern num:{glitchDic['patternNum']}")

        
    else:
        inputCol = str(args[0]).split(",")
        #print(F"hello2? : {inputCol}")
        r = inputCol[0] 
        g = inputCol[1]
        b = inputCol[2]
        
        #print(F"new colour received : {r},{g},{b}")
        newCol = [int(r),int(g),int(b)]
        if r > b or b > r:
            glitchDic['isGlitchSwitchOn']=0
        #print(F"hello4? : {newCol}")
        listCol.append(newCol)
        #print(f"hello 5!!!! color list: {listCol}")

#dispatcherCol = Dispatcher()
dispatcher.map("/ear/color", filter_handler_color)
#print(f"list of colors received: {listCol}")

def clamp(num, min_value, max_value):
        num = max(min(num, max_value), min_value)
        return num
    
def volumeColor(strip,color,step=20):
    print(f"volumeColor, brightness {dicVol['volume']}")
    #step = 20
    ###fade into another color###
    step_R = (float(color[0]) - float(lastColor[0]))/step
    step_G = (float(color[1]) - float(lastColor[1]))/step
    step_B = (float(color[2]) - float(lastColor[2]))/step
    #print(f"steps colour fade is: {step_R},{step_G},{step_B}")
    
    r = int(lastColor[0])
    g = int(lastColor[1])
    b = int(lastColor[2])
    

    stepB = (dicVol['volume']-lastVol['volume'])/step
    #print(f"step: {step}")
    bright = lastVol['volume']
    for v in range(0,step):
        c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
        bright += stepB
        setBright = round(bright)
        #print(f"bright: {bright}")
        for i in range(0,LED_COUNT):
            #strip.setPixelColor(i, Color(int(color[0]),int(color[1]),int(color[2])))
            strip.setPixelColor(i, c)
            strip.setBrightness(clamp(setBright,10,255))
        strip.show()
        time.sleep(50 / 1000.0)
        r += step_R
        g += step_G
        b += step_B
        
    ##fade to brightness -50 down, then fade to same brightness?
    bright = strip.getBrightness()
    for v in range(40,0,-1):
        if(bright<0):
            break
        c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
        bright -= 6
        setBright = round(bright)
        #print(f"bright: {bright}")
        for i in range(0,LED_COUNT):
            #strip.setPixelColor(i, Color(int(color[0]),int(color[1]),int(color[2])))
            strip.setPixelColor(i, c)
            strip.setBrightness(clamp(setBright,10,255))
        strip.show()
        time.sleep(100 / 1000.0)
        #print(f"BIRHGTLOOP,nv:{int((dicVol['volume']))}, lv:{int(lastVol['volume'])}, brightStep: {stepB}, b:{setBright}, other step: {step}, color:{r},{g},{b}")

    ##then fade to same brightness?
    for v in range(0,int(40)):
        if(bright==int((dicVol['volume']))):
            break
        c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
        bright += 6
        setBright = round(bright)
        #print(f"bright: {bright}")
        for i in range(0,LED_COUNT):
            #strip.setPixelColor(i, Color(int(color[0]),int(color[1]),int(color[2])))
            strip.setPixelColor(i, c)
            strip.setBrightness(clamp(setBright,10,255))
        strip.show()
        time.sleep(100 / 1000.0)
        #print(f"2BIRHGTLOOP,nv:{int((dicVol['volume']))}, lv:{int(lastVol['volume'])}, brightStep: {stepB}, b:{setBright}, other step: {step}, color:{r},{g},{b}")
    #print(f"VOLUMELOOPvolume: {dicVol['volume']}, col: {color}")
    lastVol['volume'] = dicVol['volume']
    
    lastColor[0] = clamp(int(color[0]),0,255)
    lastColor[1] = clamp(int(color[1]),0,255)
    lastColor[2] = clamp(int(color[2]),0,255)
    
def volumeColorSplodge(strip,color,step=20):
    print(f"volumeColorSplodge, brightness {dicVol['volume']}")

    posRandom = random.randrange(LED_COUNT)

    for a in range(0,LED_COUNT):
        strip.setPixelColor(a,Color(0,0,0))
    
    stepB=int(lastVol['volume'])/10
    bright = 0
    for v in range(0,int(10)):
        if(bright==int((lastVol['volume']))):
            break
        #c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
        bright += stepB
        setBright = round(bright)
        #print(f"bright: {bright}")
        for i in range(clamp(posRandom,0,250),clamp(posRandom+50,50,300)):
            strip.setPixelColor(i, Color(int(lastColor[0]),int(lastColor[1]),int(lastColor[2])))
            #strip.setPixelColor(i, c)
            strip.setBrightness(clamp(setBright,10,255))
        strip.show()
        time.sleep(100 / 1000.0)

    posList = [10,20,40,50,60,100,150,180,240,260]
    positions = sample(posList,3)
    
    pos = positions[0]
    pos2 = positions[1]
    pos3 = positions[2]
    
    #step = 20
    ###fade into another color###
    step_R = (float(color[0]) - float(lastColor[0]))/step
    step_G = (float(color[1]) - float(lastColor[1]))/step
    step_B = (float(color[2]) - float(lastColor[2]))/step
    #print(f"steps colour fade is: {step_R},{step_G},{step_B}")
    
    r = int(lastColor[0])
    g = int(lastColor[1])
    b = int(lastColor[2])
    

    stepB = (dicVol['volume']-lastVol['volume'])/step
    #print(f"step: {step}")
    bright = lastVol['volume']
    for v in range(0,step):
        c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
        bright += stepB
        setBright = round(bright)
        #print(f"bright: {bright}")
        for i in range(clamp(posRandom,0,300),clamp(posRandom+50,50,300)):
            #strip.setPixelColor(i, Color(int(color[0]),int(color[1]),int(color[2])))
            strip.setPixelColor(i, c)
            strip.setBrightness(clamp(setBright,10,255))
        strip.show()
        time.sleep(50 / 1000.0)
        r += step_R
        g += step_G
        b += step_B
        
    ##fade to brightness -50 down, then fade to same brightness?
    bright = strip.getBrightness()
    for v in range(40,0,-1):
        if(bright<0):
            break
        c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
        bright -= 6
        setBright = round(bright)
        #print(f"bright: {bright}")
        for i in range(clamp(posRandom,0,300),clamp(posRandom+50,50,300)):
            #strip.setPixelColor(i, Color(int(color[0]),int(color[1]),int(color[2])))
            strip.setPixelColor(i, c)
            strip.setBrightness(clamp(setBright,10,255))
        strip.show()
        time.sleep(100 / 1000.0)
        #print(f"BIRHGTLOOP,nv:{int((dicVol['volume']))}, lv:{int(lastVol['volume'])}, brightStep: {stepB}, b:{setBright}, other step: {step}, color:{r},{g},{b}")

    ##then fade to same brightness?
    for v in range(0,int(40)):
        if(bright==int((dicVol['volume']))):
            break
        c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
        bright += 6
        setBright = round(bright)
        #print(f"bright: {bright}")
        for i in range(clamp(posRandom,0,300),clamp(posRandom+50,50,300)):
            #strip.setPixelColor(i, Color(int(color[0]),int(color[1]),int(color[2])))
            strip.setPixelColor(i, c)
            strip.setBrightness(clamp(setBright,10,255))
        strip.show()
        time.sleep(100 / 1000.0)
        #print(f"2BIRHGTLOOP,nv:{int((dicVol['volume']))}, lv:{int(lastVol['volume'])}, brightStep: {stepB}, b:{setBright}, other step: {step}, color:{r},{g},{b}")
    #print(f"VOLUMELOOPvolume: {dicVol['volume']}, col: {color}")
    lastVol['volume'] = dicVol['volume']
    
    lastColor[0] = clamp(int(color[0]),0,255)
    lastColor[1] = clamp(int(color[1]),0,255)
    lastColor[2] = clamp(int(color[2]),0,255)

def cyclon(strip,color,eyeSize=50, speedDelay=30, returnDelay=100):
    print(f"cyclon curCol:{color}, brightness:{dicVol['volume']}")
    level1Max = 100
    level1Min = 0
    level2Max = 200
    level2Min = 100
    level3Max = 300
    level3Min = 200
    strip.setBrightness(clamp(dicVol['volume'],10,255))
    
    for i in range(level1Min,level1Max-eyeSize-2):
        #for x in range(level1Min,level1Max):
            #strip.setPixelColor(x, Color(0,0,0))

        strip.setPixelColor(i,Color(clamp(int(color[0]/10),0,255),clamp(int(color[1]/10),0,255),clamp(int(color[2]/10),0,255)))
        for j in range(1,eyeSize):
            strip.setPixelColor(i+j,Color(color[0],color[1],color[2]))
        strip.setPixelColor(i+eyeSize+1,Color(color[0],color[1],color[2]))
        strip.show()
        time.sleep(speedDelay/1000.0)
       #####2 
    for i in range(level2Min,level2Max-eyeSize-2):
        #for x in range(level2Min,level2Max):
         #   strip.setPixelColor(x, Color(0,0,0))

        strip.setPixelColor(i,Color(clamp(int(color[0]/10),0,255),clamp(int(color[1]/10),0,255),clamp(int(color[2]/10),0,255)))
        for j in range(1,eyeSize):
            strip.setPixelColor(i+j,Color(color[0],color[1],color[2]))
        strip.setPixelColor(i+eyeSize+1,Color(color[0],color[1],color[2]))
        strip.show()
        time.sleep(speedDelay/1000.0)
        ######2
    #####3
    for i in range(level3Min,level3Max-eyeSize-2):
        #for x in range(level3Min,level3Max):
         #   strip.setPixelColor(x, Color(0,0,0))

        strip.setPixelColor(i,Color(clamp(int(color[0]/10),0,255),clamp(int(color[1]/10),0,255),clamp(int(color[2]/10),0,255)))
        for j in range(1,eyeSize):
            strip.setPixelColor(i+j,Color(color[0],color[1],color[2]))
        strip.setPixelColor(i+eyeSize+1,Color(color[0],color[1],color[2]))
        strip.show()
        time.sleep(speedDelay/1000.0)
        ######2
    time.sleep(returnDelay/1000.0)
    
    bright=strip.getBrightness()
    for v in range(0,int(40)):
        if(bright==int((dicVol['volume']))):
            break
        #c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
        bright += 6
        setBright = round(bright)
        #print(f"bright: {bright}")
        for i in range(0,LED_COUNT):
            #strip.setPixelColor(i, Color(int(color[0]),int(color[1]),int(color[2])))
            #strip.setPixelColor(i, c)
            strip.setBrightness(clamp(setBright,10,255))
        strip.show()
        time.sleep(100 / 1000.0)
    
    #for i in range(level1Max-eyeSize-2,level1Min,-1):
        #print(f"other {i}")
     #   for x in range(0,300):
      #      strip.setPixelColor(x, Color(0,0,0))
       #     strip.setBrightness(255)
        
 #       strip.setPixelColor(i,Color(clamp(int(color[0]/10),0,255),clamp(int(color[1]/10),0,255),clamp(int(color[2]/10),0,255)))
  #      for j in range(1,eyeSize):
   #         strip.setPixelColor(i+j,Color(color[0],color[1],color[2]))
        
 #       strip.setPixelColor(i+eyeSize+1,Color(color[0],color[1],color[2]))
  #      strip.show()
   #     time.sleep(speedDelay/1000.0)
            
def volumeColorFullStrip(strip,color,step=20):
    #step = 20
    ###fade into another color###
    step_R = (float(color[0]) - float(lastColor[0]))/step
    step_G = (float(color[1]) - float(lastColor[1]))/step
    step_B = (float(color[2]) - float(lastColor[2]))/step
    #print(f"steps colour fade is: {step_R},{step_G},{step_B}")
    
    r = int(lastColor[0])
    g = int(lastColor[1])
    b = int(lastColor[2])
    

    stepB = (dicVol['volume']-lastVol['volume'])/step
    #print(f"step: {step}")
    bright = lastVol['volume']
    for v in range(0,step):
        c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
        bright += stepB
        setBright = round(bright)
        #print(f"bright: {bright}")
        for i in range(0,LED_COUNT):
            #strip.setPixelColor(i, Color(int(color[0]),int(color[1]),int(color[2])))
            strip.setPixelColor(i, c)
            strip.setBrightness(clamp(setBright,10,255))
        strip.show()
        time.sleep(50 / 1000.0)
        r += step_R
        g += step_G
        b += step_B
        #print(f"BIRHGTLOOP,nv:{int((dicVol['volume']))}, lv:{int(lastVol['volume'])}, brightStep: {stepB}, b:{setBright}, other step: {step}, color:{r},{g},{b}")
    #print(f"VOLUMELOOPvolume: {dicVol['volume']}, col: {color}")
    lastVol['volume'] = dicVol['volume']
    
    lastColor[0] = clamp(int(color[0]),0,255)
    lastColor[1] = clamp(int(color[1]),0,255)
    lastColor[2] = clamp(int(color[2]),0,255)

        
def colorPuddleFade(strip, color, step=3, wait_ms=50):
        print(f"colorPuddleFade, brightness {dicVol['volume']}")

       # for i in range(0,300):
        #    strip.setPixelColor(i, Color(0,0,0))
         #   strip.setBrightness(255)
        #strip.show()
        #time.sleep(50 / 1000.0)
        posList = [10,20,40,50,60,100,150,180,240,260]
        positions = sample(posList,3)
        
        #pos = random.randrange(LED_COUNT)
        #pos2 = random.randrange(LED_COUNT)
        #pos3 = random.randrange(LED_COUNT)
        pos = positions[0]
        pos2 = positions[1]
        pos3 = positions[2]
        print(f"currentCol: {color}, lastCol: {lastColor}, vol: {dicVol['volume']}")

#brightnessStep = int(clamp((float(dicVol['volume'])/255),1,255))*3
        potBrightness = setBrightness = 0
        bStep = (float(dicVol['volume'])/(255/step))
        #print(f"potBrightness = {potBrightness} bStep {bStep}, setB = {setBrightness} fade vol is: {dicVol['volume']} and step : {step}")
        for j in range(0,255,step):
            potBrightness += bStep
            setBrightness = round(potBrightness)
            #print(f"potBrightness = {potBrightness}, setB: {setBrightness}, Bstep: {bStep}")
            for i in range(pos,pos+30):
                strip.setPixelColor(i, Color(int(lastColor[0]),int(lastColor[1]),int(lastColor[2])))
                strip.setBrightness(clamp(int(setBrightness),0,dicVol['volume']))
                #print(f"strip b: {strip.getBrightness()} and max {dicVol['volume']}")            
            for i in range(pos2,pos2+30):
                strip.setPixelColor(i, Color(int(lastColor[0]),int(lastColor[1]),int(lastColor[2])))
                strip.setBrightness(clamp(int(setBrightness),0,dicVol['volume']))
                #print(f"strip b: {strip.getBrightness()} and max {dicVol['volume']}")            
            for i in range(pos3,pos3+30):
                strip.setPixelColor(i, Color(int(lastColor[0]),int(lastColor[1]),int(lastColor[2])))
                strip.setBrightness(clamp(int(setBrightness),0,dicVol['volume']))
                #print(f"strip b: {strip.getBrightness()} and max {dicVol['volume']}")
            strip.show()
        time.sleep(50 / 1000.0)
            
        ###fade into another color###
        step_R = (float(color[0]) - float(lastColor[0]))/255
        step_G = (float(color[1]) - float(lastColor[1]))/255
        step_B = (float(color[2]) - float(lastColor[2]))/255
        #print(f"steps colour fade is: {step_R},{step_G},{step_B}")
        r = int(lastColor[0])
        g = int(lastColor[1])
        b = int(lastColor[2])

        
        for j in range(255,0,-(step)):
            ##colour fade
            c = Color(int(clamp(r,0,255)), int(clamp(g,0,255)), int(clamp(b,0,255)))
            #print(f"new colour fade is: {r},{g},{b}")
            ##
            potBrightness -= bStep
            setBrightness = round(potBrightness)
            #print(f"potBrightness = {potBrightness}, setB: {setBrightness}, Bstep: {bStep}")
            for i in range(pos,pos+30):
                strip.setPixelColor(i, c)
                strip.setBrightness(clamp(int(setBrightness),0,dicVol['volume']))
                #print(f"strip b: {strip.getBrightness()} and max {dicVol['volume']}")
            
            for i in range(pos2,pos2+30):
                strip.setPixelColor(i, c)
                strip.setBrightness(clamp(int(setBrightness),0,dicVol['volume']))
                #print(f"strip b: {strip.getBrightness()} and max {dicVol['volume']}")
                
            for i in range(pos3,pos3+30):
                strip.setPixelColor(i, c)
                strip.setBrightness(clamp(int(setBrightness),0,dicVol['volume']))
                #print(f"strip b: {strip.getBrightness()} and max {dicVol['volume']}")

            strip.show()
            r += step_R
            g += step_G
            b += step_B
        
        for i in range(0,300):
            strip.setPixelColor(i, Color(0,0,0))
            strip.setBrightness(255)
        strip.show()
        time.sleep(50 / 1000.0)
        lastColor[0] = clamp(int(color[0]),0,255)
        lastColor[1] = clamp(int(color[1]),0,255)
        lastColor[2] = clamp(int(color[2]),0,255)

def startFromMiddleOG(strip, color, wait_ms=40):
    print(f"startFromMiddle, brightness {dicVol['volume']}")
    #color = Color(color[0],color[1],color[2])
    strip.setBrightness(dicVol['volume'])
    chance = random.randrange(0,2)
    print(f"chance:{chance}")
    for i in range(0,150):
        strip.setPixelColor(150+i, Color(int(color[0]),int(color[1]),int(color[2])))
        strip.setPixelColor(150+i+1, Color(int(color[0]/2),int(color[1]/2),int(color[2]/2)))
        strip.setPixelColor(150+i+2, Color(int(color[0]/2),int(color[1]/2),int(color[2]/2)))
        strip.setPixelColor(150+i+3, Color(int(color[0]/2),int(color[1]/2),int(color[2]/2)))
        strip.setPixelColor(150-i, Color(int(color[0]),int(color[1]),int(color[2])))
        strip.setPixelColor(150-i-1, Color(int(color[0]/2),int(color[1]/2),int(color[2]/2)))
        strip.setPixelColor(150-i-2, Color(int(color[0]/2),int(color[1]/2),int(color[2]/2)))
        strip.setPixelColor(150-i-3, Color(int(color[0]/2),int(color[1]/2),int(color[2]/2)))
        strip.show()
        time.sleep(wait_ms/1000.0)
        if(chance == 0):
            strip.setPixelColor(150+i, Color(0,0,0))
            strip.setPixelColor(150-i, Color(0,0,0))
            strip.setPixelColor(149-i, Color(0,0,0))
            strip.setPixelColor(150+i+1, Color(0,0,0))
            strip.show()
        
                
def theaterChase(strip, color, wait_ms=50, iterations=10):
        print(f"TheaterChase, brightness {dicVol['volume']}")

        """Movie theater light style chaser animation. strip.numPixels()"""
        color = Color(clamp(currentColor[0],20,255),clamp(currentColor[1],20,255),clamp(currentColor[2],20,255))
        print(f"theater chase glitch: currentcol:{currentColor}")
        strip.setBrightness(dicVol['volume'])
        for j in range(iterations):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    try:
                        strip.setPixelColor(i + q, color)
                    except OverflowError as oe:
                        strip.setPixelColor(i + q, Color(255,0,255))
                        print(f"overflowError handled")
                strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i + q, 0)
        for i in range(150,0,-1):
            strip.setBrightness(i)
            strip.show()

def colorWipeOG(strip, color, wait_ms=5):
    print(f"colorWipeOG, brightness {dicVol['volume']}")
    color = Color(color[0],color[1],color[2])
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.setBrightness(dicVol['volume'])
        strip.show()
        time.sleep(wait_ms / 1000.0)
    
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
        #strip.setBrightness(255)
        strip.show()
        time.sleep(wait_ms / 1000.0)
    currentColor[0]-=10
    currentColor[0] = clamp(currentColor[0],10,255)
    currentColor[1]-=10
    currentColor[1] = clamp(currentColor[1],10,255)
    currentColor[2]-=10
    currentColor[2] = clamp(currentColor[2],10,255)
    print(f"currentCol clamped {currentColor}")

   
# Create NeoPixel object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

async def loop():
    while True:
        if len(listCol) != 0:
            for i in range(len(listCol)):
                color = Color(listCol[i][0],listCol[i][1],listCol[i][2])
                currentColor = listCol[i]
                
                print(f"lastcol: {lastColor}, current col:{currentColor}, lastV: {lastVol}, currentV: {dicVol['volume']}")
                if glitchDic['isGlitchSwitchOn']==0:
                        #colorPuddleFade(strip,currentColor)
                        #cyclon(strip,currentColor)
                        if(glitchDic['patternNum']==0):
                            volumeColor(strip,currentColor,60)
                        elif(glitchDic['patternNum']==1):
                            startFromMiddleOG(strip,currentColor)
                            volumeColor(strip,currentColor,60)

                        #volumeColorSplodge(strip,currentColor,60)
                else:
                    print("glitch added")
                    theaterChase(strip,currentColor,clamp(int(dicVol['volume']/2),30,150),10)
            listCol.clear()
        else:
            print(f"deflastcol: {lastColor}, current col:{currentColor}, lastV: {lastVol}, currentV: {dicVol['volume']}")
            if glitchDic['isGlitchSwitchOn']==0:
                    if currentColor[0]==255 or currentColor[1]==255 or currentColor[2]==255:
                        theaterChase(strip,currentColor)
                        colorWipeOG(strip,currentColor)
                        currentColor[0] -= 10
                        currentColor[1] -= 10
                        currentColor[2] -= 10
                        currentColor = [clamp(currentColor[0],0,255),clamp(currentColor[1],0,255),clamp(currentColor[2],0,255)]
                        colorPuddleFade(strip, currentColor)
                        #startFromMiddle(strip,currentColor)
                    else:
                        if(glitchDic['patternNum']==0):
                            volumeColor(strip,currentColor,60)
                        elif(glitchDic['patternNum']==1):
                            #startFromMiddleOG(strip,currentColor)
                            volumeColor(strip,currentColor,60)
                        elif(glitchDic['patternNum']==2):
                            #startFromMiddleOG(strip,currentColor)
                            volumeColorSplodge(strip,currentColor,60)

                        #colorPuddleFade(strip, currentColor)
                        #volumeColor(strip,currentColor,60)
                        #cyclon(strip,currentColor)
            else:
                print("default loop, glitch mode")
                theaterChase(strip,currentColor,clamp(int(dicVol['volume']/2),30,255),10)
                volumeColorSplodge(strip,currentColor,60)

        await asyncio.sleep(1)

async def init_main():
    server = AsyncIOOSCUDPServer((ip, receiverPort), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    await loop()  # Enter main loop of program

    transport.close()  # Clean up serve endpoint


print("Starting")
asyncio.run(init_main())

           

