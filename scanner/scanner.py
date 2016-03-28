#!/usr/bin/python
from sys import argv
import zbar

import Hardware

# create LED object
led = Hardware.LED()

# create a Processor
proc = zbar.Processor()

# configure the Processor
proc.parse_config('enable')

# initialize the Processor
device = '/dev/video0'
if len(argv) > 1:
    device = argv[1]

proc.init(device)


# setup a callback
def my_handler(proc, image, closure):
    # extract results
    print len(image.symbols)
    led.ON([1, 1,0])  # gets stuck here ...!!!!!WTF
    '''
    if len(image.symbols) >= 1:
        led.ON([0, 1, 0])  # green
    else:
        led.ON([1, 0, 0])  # red
    '''
    print "does it get here?"
    for symbol in image.symbols:
        # do something useful with results
        print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data

proc.set_data_handler(my_handler)

led.cleanup()  # make sure to cleanup GPIO pins

# enable the preview window
proc.visible = True

# initiate scanning
proc.active = True

try:
    # keep scanning until user provides key/mouse input
    proc.user_wait()
except zbar.WindowClosed, e:
    pass
