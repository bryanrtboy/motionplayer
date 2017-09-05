#!/usr/bin/python
from subprocess import Popen
import RPi.GPIO as GPIO
import time
import os
import random

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(17, GPIO.IN)			#Read button

sleeptime =0
intruderAlert= False
startime = time.time()

cmd = "omxplayer /mnt/usb/flower.mp4 --loop --no-osd --win 100,100,740,460"
#cmd = "omxplayer /mnt/usb/flower.mp4 --loop --no-osd"
omxp = Popen ([cmd], shell=True)

isRunning = True

def PlayMovieAt(pos) :
	global startime
	cmd = "~/dbuscontrol.sh setposition " + pos
	Popen([cmd], shell=True)
	startime = time.time()

def TogglePause() :
	cmd = "~/dbuscontrol.sh pause"
	Popen([cmd], shell=True)

try:

	while isRunning:
			
		t = int(round( time.time() - startime))
		
		if t >= 8 and intruderAlert == False : #manually loop after 10 seconds
			PlayMovieAt("0")
			
		i=GPIO.input(18)
		button_value = GPIO.input(17)
		
		if i==1:                 #When output from motion sensor is LOW
			print ("No intruders")
			sleeptime += 1
			time.sleep(1)
		elif i == 0:               #When output from motion sensor is HIGH
			print ("Intruder detected")
			sleeptime = 0
			if intruderAlert == False :
				print ("Play hide section")
				PlayMovieAt("10000000")
				intruderAlert=True
				time.sleep(2) #wait for hide animation to complete playing
				TogglePause()
			time.sleep(1) #delay before checking sensors again
			 
		if intruderAlert == True and sleeptime >= 3 : #sleep is added each time no intruder is sensedqqq
			sleeptime=0
			intruderAlert=False
			TogglePause() #unpause the movie now that person is gone, movie will end and loop to beginning
			time.sleep(6.5)#wait for ending animation to complete before checking sensors again.
			
		if button_value == False:
			print('The button 2 has been pressed...\r')
			#time.sleep(2)
			isRunning = False
			#time.sleep(5)
			#os.system("sudo shutdown -h now")
			while button_value == False:
				button_value = GPIO.input(17)

		
except KeyboardInterrupt:
	print("Quit")
	GPIO.cleanup()
	time.sleep(1)
