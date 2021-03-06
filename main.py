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
hitCount = 0
maxHits = 10

#cmd = "omxplayer /home/pi/relic/flower3.mp4 --loop --no-osd --win 300,100,600,300"
cmd = "omxplayer /home/pi/relic/flower3.mp4 --loop --no-osd --aspect-mode stretch"
omxp = Popen ([cmd], shell=True)

isRunning = True

def PlayMovieAt(pos) :
	global startime
	cmd = "/home/pi/dbuscontrol.sh setposition " + pos
	Popen([cmd], shell=True)
	startime = time.time()

def TogglePause() :
	cmd = "/home/pi/dbuscontrol.sh pause"
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
        time.sleep(1)
        os.system("sudo shutdown -h now") #need to keep this because omxplayer is not quitting properly...

def RewindMovie() :
	PlayMovieAt("0")
	startime = time.time()

try:

	while isRunning:
		button_value = GPIO.input(17)
		
		distance = measure_average()
#		print ("Distance : %.1f" % distance) 
		
		if distance < 60 :
			intruder = True
		else :
			hitCount += 1
			if hitCount > maxHits :
				intruder = False
				hitCount=0
			
		t = int(round( time.time() - startime))
		
		if intruder == False : 
			if isPlayingPause == True :
				TogglePause()
				time.sleep(3.9) #unpause and play a bit before reset
				isPlayingPause = False
				RewindMovie()
				
			if t > 15 : #manually loop after 15 seconds
				RewindMovie()
		elif isPlayingPause == False :
#			print("Intruder Alert!")
			isPlayingPause = True
			if random.random() > .5 :
				PlayMovieAt("24000000")
			else :
				PlayMovieAt("16000000")
			time.sleep(4.5) #When True, will only pause after x seconds
			TogglePause()
			
			
		if button_value == False:
#			print('The button 2 has been pressed...\r')
			isRunning = False
			Quit()
			time.sleep(1)
			#os.system("sudo shutdown -h now")
			while button_value == False:
				button_value = GPIO.input(17)
		time.sleep(.1)
		
except KeyboardInterrupt:
	Quit()
	

