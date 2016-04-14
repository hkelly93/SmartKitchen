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
    # TODO allow colors to dim to get better color range
    def __init__(self, pin_r=11, pin_g=13, pin_b=15):
        super(RGB_LED, self).__init__(pin_r)

        # pin values most likely will be changed

        self.colors = [pin_r, pin_g, pin_b]

        # setup the pins to output
        for pin in self.colors:
            #print pin
            GPIO.setup(pin, GPIO.OUT)

        self.freq = 100  # Hz

        self.RED = GPIO.PWM(self.colors[0], self.freq)
        self.GREEN = GPIO.PWM(self.colors[1], self.freq)
        self.BLUE = GPIO.PWM(self.colors[2], self.freq)

        self.RED.start(0)
        self.GREEN.start(0)
        self.BLUE.start(0)

    def color(self, (R, G, B), on_time=1):
        #print 'set color'
        # colour brightness range is 0-100
        self.RED.ChangeDutyCycle(R)
        self.GREEN.ChangeDutyCycle(G)
        self.BLUE.ChangeDutyCycle(B)
        time.sleep(on_time)

        self.RED.ChangeDutyCycle(0)
        self.GREEN.ChangeDutyCycle(0)
        self.BLUE.ChangeDutyCycle(0)

    def off(self):

        self.RED.stop()
        self.GREEN.stop()
        self.BLUE.stop()

        self.cleanup()


class Buzzer(object):
    pass


if TEST:
    led = RGB_LED()
    led.color(100, 20, 0, 10)
    led.off()


