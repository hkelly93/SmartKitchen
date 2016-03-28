#!/usr/bin/python
from sys import argv
import os
import zbar
import time

import requests

pi = None
# determine if this is running on pi or other os
if os.uname()[4][:3] == 'arm':
    # for LED
    try:
        from Hardware import RGB_LED
        import RPi.GPIO as GPIO
        pi = True
    except ImportError:
        pi = False
        pass

TEST = True  # for prototyping only

# TODO need to post barcode to this url
#r = requests.post('http://localhost:5000/addInventory/ #barcode # /)

class Scanner(object):
    """
    Turns on LED and camera to search through live video feed and look for a barcode

    """
    FLAG = False  # used to trigger LED for status

    def __init__(self):
        if pi:
            # create LED object
            self.led = RGB_LED()
            self.data = None

            self.led.on([1, 0, 0])  # Red defaulted

        # create a Processor
        self.proc = zbar.Processor()
    
        # configure the Processor
        self.proc.parse_config('enable')
    
        # initialize the Processor
        device = '/dev/video1'
        if len(argv) > 1:
            device = argv[1]
    
        self.proc.init(device)

        self.proc.set_data_handler(self.my_handler)

        # enable the preview window
        self.proc.visible = True
    
        # initiate scanning
        self.proc.active = True

        self.run()

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, val):
        self.__data = val

    def next_barcode(self):
        # will be empty if no barcode scanned
        self.__init__()
        return self.data()

    def my_handler(self, proc, image, closure): # setup a callback
        global FLAG
        # extract results
        for symbol in image.symbols:
            FLAG = True
            # print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
            self.__data = "%s" % symbol.data

    def status_barcode_accepted(self):
        global FLAG
        print "barcode decoded"
        self.led.on([0, 1, 0])
        time.sleep(2) # TODO probably need to adjust this time
        self.led.off()
        FLAG = False

        self.led.cleanup()

    def run(self):
        global pi
        # this loop can probably be removed from here and put in the main code
        try:
            # keep scanning until window is closed
            # should stop when user sends command to stop or times out
            self.proc.process_one() # can only scan one barcode at a time
            # print "after user_wait"
            if FLAG:
                if pi:
                    self.status_barcode_accepted()

        except zbar.WindowClosed, e:
            if pi:
                self.led.cleanup()
            pass

if TEST:
    # should loop until user clocks stop on UI
    loop = 3
    start = Scanner()
    print 'barcode 1: ' + start.data

    for i in xrange(loop):
        time.sleep(2)
        start.next_barcode()
        print 'barcode ' + str(i+2) + ': ' + start.data
