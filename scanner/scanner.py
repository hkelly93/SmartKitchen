#!/usr/bin/python
from sys import argv
import zbar
import time
from Hardware import RGB_LED

# for LED
import RPi.GPIO as GPIO

TEST = True  # for prototyping only


class Scanner(object):
    """
    Turns on LED and camera to search through live video feed and look for a barcode

    """
    FLAG = False  # used to trigger LED for status

    def __init__(self):
        # create LED object
        self.led = RGB_LED()
        self.data = None

        self.led.on([1, 0, 0])  # Red defaulted

        # create a Processor
        self.proc = zbar.Processor()
    
        # configure the Processor
        self.proc.parse_config('enable')
    
        # initialize the Processor
        device = '/dev/video0'
        if len(argv) > 1:
            device = argv[1]
    
        self.proc.init(device)

        self.proc.set_data_handler(self.my_handler)

        # enable the preview window
        self.proc.visible = False
    
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
        self.__init__()

    def my_handler(self, proc, image, closure): # setup a callback
        global FLAG
        # extract results
        for symbol in image.symbols:
            FLAG = True
            # print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
            self.__data = "%s" % symbol.data

    def status_barcode_accepted(self):
        global FLAG
        self.led.on([0, 1, 0])
        time.sleep(1)
        self.led.off()
        FLAG = False

        self.led.cleanup()

    def run(self):
        # this loop can probably be removed from here and put in the main code
        try:
            # keep scanning until user provides key/mouse input
            # self.proc.user_wait() # trying to use this but never triggers LED
            self.proc.process_one() # can only scan one barcode at a time
            #print "after user_wait"
            if FLAG:
                self.status_barcode_accepted()

        except zbar.WindowClosed, e:
            self.led.cleanup()
            pass

if TEST:
    # should loop until user clocks stop on UI
    loop = 3
    start = Scanner()
    print 'barcode 1: ' + start.data

    for i in xrange(loop):
        start.next_barcode()
        print 'barcode ' + str(i+2) + ': ' + start.data
