#!/usr/bin/python
from subprocess import Popen
import RPi.GPIO as GPIO
import time
import os
import random

GPIO.setwarnings(False)

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_TRIGGER = 23
GPIO_ECHO    = 24

print ("Ultrasonic Measurement")

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER, False)

GPIO.setup(17, GPIO.IN)			#Read button

intruder= False
startime = time.time()
isPlayingPause = False

cmd = "omxplayer /home/pi/relic/flower.mp4 --loop --no-osd --win 100,100,740,460"
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
	
def measure():
	# This function measures a distance
	GPIO.output(GPIO_TRIGGER, True)
	time.sleep(0.00001)
	GPIO.output(GPIO_TRIGGER, False)
	start = time.time()
	
	while GPIO.input(GPIO_ECHO)==0:
		start = time.time()
	
	while GPIO.input(GPIO_ECHO)==1:
		stop = time.time()
	
	elapsed = stop-start
	distance = (elapsed * 34300)/2
	
	return distance
  
def measure_average():
	# This function takes 3 measurements and
	# returns the average.
	distance1=measure()
	time.sleep(0.1)
	distance2=measure()
	time.sleep(0.1)
	distance3=measure()
	distance = distance1 + distance2 + distance3
	distance = distance / 3
	return distance
	
def Quit() :
	print("Quit")
	GPIO.cleanup()

def RewindMovie() :
	PlayMovieAt("0")
	startime = time.time()

try:

	while isRunning:
		button_value = GPIO.input(17)
		
		distance = measure_average()
		print ("Distance : %.1f" % distance) 
		
		if distance < 40 :
			intruder = True
		else :
			intruder = False
			
		t = int(round( time.time() - startime))
		
		if intruder == False : 
			if isPlayingPause == True :
				TogglePause()
				isPlayingPause = False
				RewindMovie()
				
			if t > 7 : #manually loop after 10 seconds
				RewindMovie()
		else :
			if isPlayingPause == False :
				print("Intruder Alert!")
				isPlayingPause = True
				PlayMovieAt("10000000")
				time.sleep(2.5) #When True, will only unpause after 2 seconds
				TogglePause()
			
			
		if button_value == False:
			print('The button 2 has been pressed...\r')
			isRunning = False
			Quit()
			#time.sleep(1)
			#os.system("sudo shutdown -h now")
			while button_value == False:
				button_value = GPIO.input(17)
		time.sleep(.1)
		
except KeyboardInterrupt:
	Quit()
	

