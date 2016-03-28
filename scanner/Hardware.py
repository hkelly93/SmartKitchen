#!/usr/bin/python
import RPi.GPIO as GPIO
import time

TEST = False

class LED(object):
    """
    should set these up to use PWM
    """
    def __init__(self, pin=7):
        GPIO.setmode(GPIO.BOARD)  # physical pin numbers

        # pin values most likely will be changed
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)

    def on(self, val):
        GPIO.output(self.pin, val)

    def off(self):
        GPIO.output(self.pin, 0)

    @staticmethod
    def cleanup():
        # this must be called or lights will stay on after code is executed
        GPIO.cleanup()

class RGB_LED(LED):
    def __init__(self, pin_r=11, pin_g=13, pin_b=15):
        super(RGB_LED,self).__init__(pin_r)

        # pin values most likely will be changed
        self.red = self.pin
        self.green = pin_g
        self.blue = pin_b
        self.colors = [self.red, self.green, self.blue]

        # setup the pins to output
        for pin in self.colors:
            GPIO.setup(pin, GPIO.OUT)
            # GPIO.output(pin, 0)

    def on(self, color): #, color=[1, 1, 1]):
        for i, pin in enumerate(self.colors):
             GPIO.output(pin, color[i])

    def off(self):
        for pin in self.colors:
             GPIO.output(pin, 0)


class Buzzer(object):
    pass


if TEST:
    led = RGB_LED()
    led.ON([0,1,0])

    time.sleep(3)
    led.OFF()

    time.sleep(2)
    led.ON([1,0,0])
    time.sleep(3)
    led.OFF()

    led.cleanup()


