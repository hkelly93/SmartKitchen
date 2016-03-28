#!/usr/bin/python
from sys import argv
import os
import zbar
import time

TEST = False  # for prototyping only


class Scanner(object):
    """
    Turns on Lcamera to search through live video feed and look for a barcode
    #TODO would like to keep this running and not shutodwn after every barcode

    """
    def __init__(self):
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

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, val):
        self.__data = val

    def my_handler(self, proc, image, closure): # setup a callback
        global FLAG
        # extract results
        for symbol in image.symbols:
            FLAG = True
            # print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
            self.__data = "%s" % symbol.data

    def get_barcode(self):
        # keeps scanning until window is closed or barcode is found
        # should allow this to time out or user to cancel
        try:
            # should stop when user sends command to stop or times out
            self.proc.process_one()  # can only scan one barcode at a time

        except zbar.WindowClosed, e:
            # TODO should catch exception for user canceling
            print "exception: should have more detailed info"
            pass

        return self.data

if TEST:
    # should loop until user clocks stop on UI
    loop = 3
    start = Scanner()
    print 'barcode 1: ' + start.data

    for i in xrange(loop):
        time.sleep(2)
        start.get_barcode()
        print 'barcode ' + str(i+2) + ': ' + start.data
