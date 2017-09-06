#!/usr/bin/python
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN)         #Read output from PIR motion sensor

while True:
       i=GPIO.input(23)
       if i==0:                 #When output from motion sensor is LOW
             print "No intruders",i
             time.sleep(.1)
       elif i==1:               #When output from motion sensor is HIGH
             print "Intruder detected",i
             time.sleep(.1)
