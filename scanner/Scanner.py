# TODO could use socket IO to accept commands from the API instead of useing a file as a in-between
try:
    import os
    import time
    import subprocess
    import threading
    from setproctitle import setproctitle
    import requests

except ImportError as e:
    print str(e)

setproctitle('barcode_scanner')

DEBUG = True

# see if  this is running on pi or other os
if os.uname()[4][:3] == 'arm':
    try:
        from Hardware import *
        pi = True
    except ImportError:
        pi = False
        pass
else:
    pi = False


class Scanner(object):
    """

    """
    def __init__(self, url=None):
        self.run_event = threading.Event()  # if this is False then the sub threads will terminate
        self.run_event.set()

        self.status_event = threading.Event()  # true when a barcode is received
        self.status_event.clear()

        self.eco_event = threading.Event()  # False means both threads should be on
        self.eco_event.clear()

        self.server_url = url

        # threads
        self.t1 = threading.Thread(target=self.status, name='show_status')
        self.t2 = threading.Thread(target=self.scan, name='scanner')
        self.timer = TimerClass(10)

        if pi:
            self.led = RGB_LED()

        self.start()

    def start(self):
        """

        :return:
        """
        self.t1.start()  # start status thread
        self.t2.start()  # scanner thread
        self.timer.start()   # timer thread

        try:
            while True:
                print 'main thread running'

                # TODO should be checking to see if the timer finished
                # if so then power-saver should be turned on
                if self.eco_event.is_set():
                    print 'eco mode is running'
                    time.sleep(60)  # send status to rest api but not too often
                else:
                    time.sleep(10)
                    '''
                    if self.get_from_server(): # ask to see if things should turnback on
                        self.eco_event.clear()
                    '''
                    #self.post_status()  # send status

        except KeyboardInterrupt:
            print "main thread killed"
            self.shutdown()

            print "threads successfully closed"

    def scan(self):
        """
        create a zbar stream subprocess
        grabs output barcode data
        set event if barcode found
        """
        while self.run_event.is_set():
            if not self.eco_event.is_set():
                self.start_zbarcam()

                time.sleep(3)  # slight pause to allow zbarcam to kick on
                self.status_event.clear()
                if DEBUG:
                    print'scanner waiting on status event to scan again'

                while not self.status_event.is_set():

                    p = False
                    if p:
                        code = p.stdout.readline()
                        if DEBUG:
                            print 'Got barcode:', code
                        barcode = code.split(':')[1].rstrip()  # strips out type of barcode and the trailing char

                    else:
                        print 'scanner not on, using dummy data'
                        barcode = '123456789'

                    # got a barcode reset timer
                    self.timer.restart()
                    post = 'inventory/' + barcode
                    self.post_to_server(post, barcode)  # send barcode to server

                    self.status_event.set()  # valid barcode trigger green light
                    # this should cause the scanner to stop till light has been shown

            else:  # self.eco_event.is_set():
                if DEBUG:
                    print 'scanner in eco mode'
                time.sleep(10)  # create longer pauses in loops if in eco mode
        else:
            print 'scanner shutdown'

    def status(self):
        """
        displays program status on hardware
        normally should be displaying a blue light
        triggers green light for 3 seconds only if barcode is found in scan thread
        triggers pulsing red light if in eco mode
        """
        red = (100, 0, 0)
        green = (0, 100, 0)
        blue = (0, 0, 100)
        while self.run_event.is_set():
            time.sleep(1)

            if not self.eco_event.is_set():  # full power
                if self.status_event.is_set():  # if barcode is received then return a green

                    if pi:
                        self.led.color(green, 5)
                    if DEBUG:
                        time.sleep(3)
                        print 'Green led'

                    self.status_event.clear()
                else:
                    if pi:  # turn light back to blue
                        self.led.color(blue, 3)
                    if DEBUG:
                        time.sleep(3)
                        print 'Blue led'

            else:  # self.eco_event.is_set():  # TODO make this a slow pulse
                if pi:
                    self.led.color(tuple(x/2 for x in red), 0.5)
                if DEBUG:
                    time.sleep(1)
                    print 'red orb'
        else:
            print 'status shutdown'

    def post_to_server(self, uri, data):
        """

        :param uri:
        :param data:
        :return:
        """
        if self.server_url is not None:
            r = requests.post(self.server_url + uri, data=data)

            if DEBUG:
                status = r.status_code
                print r.url
                # TODO check response for 200 HTTP ok, 400 bad requests, 500 api issue
                if status == 200:
                    #print 'all good'
                    return True
                else:
                    #print status
                    return False
        else:
            print 'cant POST no server specified'

    def get_from_server(self, uri):
        """

        :param uri:
        :return:
        """
        if self.server_url is not None:
            r = requests.get(self.server_url + uri)

            if DEBUG:
                status = r.status_code
                print r.url
                # TODO check response for 200 HTTP ok, 400 bad requests, 500 api issue
                if status == 200:
                    print 'all good'
                    return True
                else:
                    print status
                    return False
        else:
            print 'cant GET, no server specified'

    @staticmethod
    def start_zbarcam():
        """

        :return:
        """
        if DEBUG:
            print 'starting up zbarcam'
        #p = subprocess.Popen(['/usr/bin/zbarcam', '--nodisplay', '/dev/video0'], stdout=subprocess.PIPE)  # run barcode scanner software
        #p = subprocess.Popen(['/usr/bin/zbarcam', '/dev/video0'], stdout=subprocess.PIPE)  # run barcode scanner software
        pass

    def post_status(self):
        """
        check status of program and return it to the rest api
        """
        if DEBUG:
            print 'Current # of threads running ' + str(threading.active_count())

        count = threading.active_count()
        if count == 3:
            status = 'healthy'
        elif count == 2:
            status = 'warning'
        else:  # only the main thread is running
            status = 'critical'
            #self.shutdown()
            self.find_process('zbarcam', True)  # only main thread, make sure zbar is dead
            if pi:
                self.led.color((100, 0, 0), 10)
            # TODO critical status should also show if this code was not running
            self.run_event.clear()

        post = 'health/scanner?status=' + status
        self.post_to_server(post, status)

    def shutdown(self):
        """

        :return:
        """
        self.run_event.clear()  # this really should be enough stop threads from running?
        self.timer.kill()  # stops
        self.find_process('zbarcam', True)

        if pi:  # shut off led
            self.led.cleanup()


        # cleanup threads will throw error if they are already killed
        self.t1.join()
        self.t2.join()
        self.timer.join()


class TimerClass(threading.Thread):
    """

    """


    def __init__(self, length):
        threading.Thread.__init__(self)
        self._DEBUG = False
        # Events start clear
        self.timer_finished = threading.Event()   # clear means keep running
        self.timer_paused = threading.Event()  # clear means timer is not paused
        self.timer_paused.set()

        self.length = length  # initial timer amount to be able to reset at same duration
        self.count = length  # current timer amount

    def run(self):
        while not self.timer_finished.is_set():
            time.sleep(.1)  # tiny pause needed to let other threads run

            if not self.timer_paused.is_set():  # not paused
                if self.count > 0:  # still need to count down
                    if DEBUG:
                        print self.count
                    self.count -= 1
                    self.timer_paused.wait(1)  # pause a second to act like a timer

                else:  # self.count == 0:
                    if DEBUG:
                        print 'timer completed'
                    self.stop()

            # this is only needed for debug purposes
            else:  # timer paused
                if self._DEBUG:
                    print 'timer paused'
                self.timer_paused.wait()

    def kill(self):
        self.timer_finished.set()

    def stop(self):
        if not self.timer_paused.is_set():  # not paused
            self.pause()
            self.reset()
        else:  # already paused
            self.reset()

    def restart(self):
        if not self.timer_paused.is_set():  # not paused
            self.reset()
        else:  # already paused
            self.reset()
            self.resume()

    def reset(self, restart=False, duration=None):
        """
        bring count of timer back up to given value
        :param restart: will start back up timer
        :param duration: in seconds, defaults to what ever the timer previously was set to
        """
        if duration is not None:
            self.count = self.length = duration
        else:
            self.count = self.length
        if self._DEBUG:
            print 'rest timer with %d seconds' % self.count

        if restart:
            self.resume()

    def pause(self):  # pauses timer until event is flagged true
        if not self.timer_paused.is_set():  # if not paused
            self.timer_paused.set()  # will pause on next loop
        if self._DEBUG:
            print 'already paused'

    def resume(self):
        if self.timer_paused.is_set():  # is paused
            self.timer_paused.clear()
        if self._DEBUG:
            print 'already running'


if __name__ == "__main__":
    scan = Scanner()  #'http://localhost:5000/')  # 'http://10.253.85.225:5000/'

