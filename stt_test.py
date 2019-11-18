#-*- coding:utf-8 -*-



import sys

reload(sys)

sys.setdefaultencoding('utf-8')


import audiostream as stt


AudioInput = stt.SpeechToText()

Red = ["빨강","빨간"]
Blue = ["파란","파랑"]
Green = ["초록"]
Yellow = ["노랑","노란"]
Purple = ["보라"]
Orange = ["주황","오렌지","오랜지"]

AudioInput = "".join(AudioInput.split(" "))

for R in Red:
    if R in AudioInput:
        print("Turn on Red")

for B in Blue:
    if B in AudioInput:
        print("Turn on Blue")

for G in Green:
    if G in AudioInput:
        print("Turn on Green")

for Y in Yellow:
    if Y in AudioInput:
        print("Turn on Yellow")

for P in Purple:
    if P in AudioInput:
        print("Turn on Yellow")

for O in Orange:
    if O in AudioInput:
        print("Turn on Orange")