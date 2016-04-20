
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)         #Read output from PIR motion sensor
#GPIO.setup(3, GPIO.OUT)         #LED output pin
while True:
    i=GPIO.input(21)
    if i==0:                 #When output from motion sensor is LOW
        print "No intruders",i
        time.sleep(0.1)
    elif i==1:               #When output from motion sensor is HIGH
        print "Intruder detected",i

        time.sleep(0.1)