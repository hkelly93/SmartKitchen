import os
import subprocess
import psutil
import threading
import requests
import time

# see if  this is running on pi or other os
if os.uname()[4][:3] == 'arm':
    try:
        from Hardware import *
        #import RPi.GPIO as GPIO should import in with Hardware
        pi = True
    except ImportError:
        pi = False
        pass

DEBUG = False


class Scanner(object):
    def __init__(self):
        self.run_event = threading.Event()  # if this is False then the sub threads will terminate
        self.run_event.set()

        self.status_event = threading.Event()  # used to control current running thread
        self.status_event.set()

        self.eco_event = threading.Event()  # False means both threads should be on
        self.eco_event.clear()

        self.server_url = 'http://localhost:5000/'

        if pi:
            self.led = RGB_LED()

        self.start()

    def start(self):
        t1 = threading.Thread(target=self.show_status, name='show_status')
        t2 = threading.Thread(target=self.scan, name='scanner')

        t2.start()
        t1.start()

        # TODO I can shut down threads after a certain time frame
        # but need to be able to turn them back on from teh outside

        # t = threading.Timer(10, timer)  # timer object for setting eco mode
        # t.start()
        try:
            while True:
                print 'main thread running'
                time.sleep(10)  # send status to rest api but not too often
                self.post_status()

                # power saver mode on? no, then restart threads that are down
                '''
                if not eco_event.is_set():  # all threads should be running
                    # check what threads are not running and recreate them
                    if not t1.is_alive():
                        print "status thread dead, restarting"
                        t1 = threading.Thread(target=show_status, name='show_status')  # , args=(i,))
                        t1.start()
                    if not t2.is_alive():
                        print "scanner thread is dead, restarting"
                        t2 = threading.Thread(target=scan, name='scanner')
                        t2.start()

                    t = threading.Timer(10, timer)  # timer object for setting eco mode
                    t.start()
                    '''
                # TODO find a way to shut down scanner thread only but leave others active for power saving

        except KeyboardInterrupt:
            print "main thread killed"
            self.shutdown()

            print "threads successfully closed"

    # def timer(self):
    #     """
    #     create a timer to shut down threads when not used for a long time
    #     after x seconds set the run_event flag to False
    #
    #     """
    #     if DEBUG:
    #         print 'TIMER TRIGGERED'
    #     self.run_event.clear()
    #     self.eco_event.set()
    #     self.shutdown()

    def post_to_server(self, uri, data):
        r = requests.post(self.server_url + uri, data=data)

        if DEBUG:
            status = r.status_code
            print r.url
            # TODO check response for 200 HTTP ok, 400 bad request, 500 api issue
            if status == 200:
                print 'all good'
                return True
            else:
                print status
                return False

    def scan(self, timeout = 0):
        """
        create a zbar stream subprocess
        grabs output barcode data
        set event if barcode found
        """
        #p = subprocess.Popen(['/usr/bin/zbarcam', '--nodisplay', '/dev/video0'], stdout=subprocess.PIPE)  # run barcode scanner software
        p = subprocess.Popen(['/usr/bin/zbarcam', '/dev/video0'], stdout=subprocess.PIPE)  # run barcode scanner software
        while self.run_event.is_set():
            time.sleep(1)  # slight pause is needed to allow other threads to show
            if DEBUG:
                print'scanner waiting on status event to scan again'

            while self.status_event.is_set():
                code = p.stdout.readline()
                if DEBUG:
                    print 'Got barcode:', code
                barcode = code.split(':')[1].rstrip()  # strips out type of barcode and the trailing char

                post = 'addInventory/' + barcode + '/'
                self.post_to_server(post, barcode)  # send barcode to server

                self.status_event.clear()  # valid barcode trigger green light
                # this should cause the scanner to stop till light has been shown

    def show_status(self):
        """
        displays program status on hardware
        should always be running
        triggers green light only if barcode is found in scan thread
        TODO triggers red light if scanner thread is no up in running
        """
        if pi:
            self.led.on([1, 1, 1])# TODO yellow light

        while self.run_event.is_set():  # not run_event.is_set:
            # print "status update here"
            if not self.status_event.is_set():  # if barcode is received then return a green
                if DEBUG:
                    print 'green light whould stay on for 3 secs here'
                if pi:
                    self.led.on([0, 1, 0])
                time.sleep(3)
                self.status_event.set()
                if pi:
                    self.led.on([1, 1, 1]) # TODO should be yellow

            elif DEBUG:
                # waiting on a barcode
                print 'yellow light'

            # TODO put another if statement to make red light flash if scanner thread is not active
            time.sleep(2)  # dont need to update the lights too often
        '''
        if not self.run_event.is_set():  # scanner must be down
            while True:
                print 'RED LIGHT '
        '''

    def post_status(self):
        """
        check status of program and return it to the rest api
        """
        if DEBUG:
            print 'post_status'
            print threading.active_count()  # will return 3 if all good

        count = threading.active_count()
        if count == 3:
            status = 'healthy'
        elif count == 2:
            status = 'warning'
        else:
            status = 'critical'
            self.kill_zbar()  # only main thread, make sure kill zbar
            if pi:
                self.led.on([1,0,0])
            # TODO critical status should also show if this code was not running
            self.run_event.clear()

        post = 'setScannerHealth/' + status + '/'
        self.post_to_server(post, status)

    @staticmethod
    def kill_zbar():
        PROCNAME = 'zbarcam'

        for proc in psutil.process_iter():
            # check whether the process name matches
            try:
                if proc.name == PROCNAME:
                    print 'killing zbarcam'
                    proc.kill()
            except:

                pass

    def shutdown(self):
        self.run_event.clear()  # this really should be enough stop threads from running?

        if pi:  # shut off led
            self.led.cleanup()

        self.kill_zbar()


        # cleanup threads
        self.t1.join()
        self.t2.join()


scan = Scanner()
