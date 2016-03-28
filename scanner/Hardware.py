#!/usr/bin/python
import RPi.GPIO as GPIO
import time

TEST = False


class LED(object):
    """

    """
    def __init__(self):
        # pin values most likely will be changed
        self.r = 11
        self.g = 13
        self.b = 15
        self.colors = [self.r, self.g, self.b]
        GPIO.setmode(GPIO.BOARD)

        # setup the pins to output
        for pin in self.colors:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def ON(self, color): #, color=[1, 1, 1]):
        print len(self.colors)
        for c in len(self.colors):
            print c

        print 'out of for loop'
        return False

    def OFF(self):
        for pin in self.colors:
             GPIO.output(pin,0)

    def cleanup(self):
        GPIO.cleanup()

if TEST:
    led = LED()
    led.ON([0,1,0])

    time.sleep(3)
    led.OFF()

    time.sleep(2)
    led.ON([1,0,0])
    time.sleep(3)
    led.OFF()

    led.cleanup()


