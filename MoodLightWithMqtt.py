# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import sys
sys.path.append('/home/pi/MoodLight/rpi_ws281x/python/build/lib.linux-armv7l-2.7')
import time
from neopixel import *
import argparse

import paho.mqtt.client as mqtt
import time

import audiostream as stt

import RPi.GPIO as GPIO

import urllib2

# LED strip configuration:
LED_COUNT      = 144      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255   # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

MQTT_SERVER = "tailor.cloudmqtt.com"
MQTT_PATH = "MoodLight/#"

ColorChanged = 0
ModeChanged = 0
PowerChanged = 0
LightPower = 0

ColorMode = 'CW'
Red = 153
Green = 0
Blue = 255

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        if ColorChanged==1 or ModeChanged==1:
            print("");
            return
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def colorWipe_A(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        if ColorChanged==1 or ModeChanged==1:
            print("");
            return
        strip.setPixelColor(i, color)
        time.sleep(wait_ms/1000.0)
    strip.show()

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        if ColorChanged==1 or ModeChanged==1 or GPIO.input(2)==0:
            return
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            if ColorChanged==1 or ModeChanged==1 or GPIO.input(2)==0:
                return
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def DimmingMode(strip,color):
    for i in range(strip.numPixels()):
        if ColorChanged==1 or ModeChanged==1 or GPIO.input(2)==0:
            print("");
            return
        strip.setPixelColor(i, color)
    strip.show()
    for i in range (0,200):
        if ColorChanged==1 or ModeChanged==1 or GPIO.input(2)==0:
            print("");
            return
        strip.setBrightness(i)
        strip.show()
        time.sleep(0.01)
    for i in range (0,200):
        if ColorChanged==1 or ModeChanged==1 or GPIO.input(2)==0:
            print("");
            return
        strip.setBrightness(200-i)
        strip.show()
        time.sleep(0.01)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global Red
    global Green
    global Blue
    global ColorChanged
    global ModeChanged
    global ColorMode
    global LightPower

    message=str(msg.payload)
    topic = msg.topic
    #print(topic+" "+message)
    if(topic=="MoodLight/Color"):
        print("Color Changed")
        red = int('0x'+message[2:4],16)
        green =int('0x'+message[4:6],16)
        blue = int('0x'+message[6:8],16)

        Red = red
        Green = green
        Blue = blue
        ColorChanged =1
        print(red,green,blue)

    if(topic == "MoodLight/Mode"):
        print("Mode change")
        LightMode = message

        if(LightMode == 'ColorWipe'):
            print("CW")
            ColorMode = 'CW'
            ModeChanged = 1
        elif(LightMode == 'TheaterChase'):
            print('TC')
            ColorMode = 'TC'
            ModeChanged = 1
        elif(LightMode == 'Rainbow'):
            print("RB")
            ColorMode = 'RB'
            ModeChanged = 1
        else:
            print("Unknown Mode")


    if(topic == "MoodLight/Power"):
        print("power changed")
        PowerMode = message
        if(PowerMode == 'on'):
            print('on')
            LightPower = 1
        elif(PowerMode == 'off'):
            print('off')
            LightPower = 0



    # more callbacks, etc

def setColorWipe(strip, color, wait_ms=50):
    global ModeChanged
    global ColorChanged
    global LightPower

    ModeChanged = 0
    ColorChanged = 0
    while ((ModeChanged == 0) and (ColorChanged==0) and (LightPower==1)and GPIO.input(2)!=0):

        colorWipe(strip, color,0)
        #time.sleep(0.5)

def settheaterChase(strip, color, wait_ms=50, iterations=10):
    global ModeChanged
    global ColorChanged
    global LightPower

    ModeChanged = 0
    ColorChanged = 0
    while ((ModeChanged == 0) and (ColorChanged==0) and (LightPower==1)and GPIO.input(2)!=0):
        #time.sleep(0.5)
        DimmingMode(strip, color)
    strip.setBrightness(255)
        #time.sleep(0.5)

def setrainbow(strip, wait_ms=20, iterations=1):
    global ModeChanged
    global ColorChanged
    global LightPower

    ModeChanged = 0
    ColorChanged = 0
    while ((ModeChanged == 0) and (ColorChanged==0) and (LightPower==1) and GPIO.input(2)!=0):

        rainbow(strip, wait_ms=20, iterations=1)

        #time.sleep(0.5)

def AImode():
    global Red
    global Green
    global Blue
    global LightPower
    global ColorMode

    AudioInput = stt.SpeechToText()

    W_Red = ["빨강","빨간"]
    W_Blue = ["파란","파랑"]
    W_Green = ["초록"]
    W_Yellow = ["노랑","노란"]
    W_Purple = ["보라"]
    W_Orange = ["주황","오렌지","오랜지"]
    W_Plant = ["화분","물"]
    W_Rainbow = ["무지개"]
    
    AudioInput = "".join(AudioInput.split(" "))

    for R in W_Red:
        if R in AudioInput:
            Red = 255
            Green = 0
            Blue = 0
            if (ColorMode == 'RB'):
                ColorMode = "CW"
            print("Turn on Red")

    for B in W_Blue:
        if B in AudioInput:
            Red =0
            Green = 0
            Blue = 255
            if (ColorMode == 'RB'):
                ColorMode = "CW"
            print("Turn on Blue")

    for G in W_Green:
        if G in AudioInput:
            Red =0
            Green = 255
            Blue = 0
            if (ColorMode == 'RB'):
                ColorMode = "CW"
            print("Turn on Green")

    for Y in W_Yellow:
        if Y in AudioInput:
            print("Turn on Yellow")
            Red =255
            Green = 255
            Blue = 0
            if (ColorMode == 'RB'):
                ColorMode = "CW"

    for P in W_Purple:
        if P in AudioInput:
            print("Turn on Yellow")
            Red =127
            Green = 0
            Blue = 255
            if (ColorMode == 'RB'):
                ColorMode = "CW"

    for O in W_Orange:
        if O in AudioInput:
            print("Turn on Orange")
            Red =255
            Green = 127
            Blue = 0
            if (ColorMode == 'RB'):
                ColorMode = "CW"

    for P in W_Plant:
        if P in AudioInput:
            print("Water Plant")
            client.publish("Arduino/Commend", "Watering", qos=0, retain=False)
    
    for R in W_Rainbow:
        if R in AudioInput:
            ColorMode = 'RB'
            
        

    if "불꺼" in AudioInput:
        print("Turn off")
        LightPower = 0

    if "불켜" in AudioInput:
        print("Turn on")
        LightPower = 1

def internet_on():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib2.URLError as err:
        return False

# Main program logic follows:\
GPIO.setmode(GPIO.BCM)
GPIO.setup(2 , GPIO.IN)
client = mqtt.Client()
client.username_pw_set("wvewfgbg", "0BwuLSnOSda4")
client.on_connect = on_connect
client.on_message = on_message
while (internet_on() == False):
    print("network error")
client.connect(MQTT_SERVER, 17298, 60)


client.loop_start();

if __name__ == '__main__':
    # Process arguments
    global Red
    global Green
    global Blue
    global ColorMode
    global LightPower

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print ('Press Ctrl-C to quit.')
    colorWipe(strip, Color(100, 100, 150),0)
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            if LightPower == 1:
                if ColorMode == 'CW':
                    setColorWipe(strip,Color(Green,Red, Blue))
                elif ColorMode == 'TC':
                    settheaterChase(strip, Color(Green,Red, Blue))
                elif ColorMode == 'RB':
                    setrainbow(strip)
                print('working')
            else:
                colorWipe(strip, Color(0, 0, 0),0)

            if GPIO.input(2)==0:
                colorWipe_A(strip, Color(100, 100, 100),0)
                AImode()
            #TODO

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)