# TODO could use socket IO to accept commands from the API instead of useing a file as a in-between
try:
    import os
    import time
    import subprocess
    import threading
    from setproctitle import setproctitle
    import requests

    import ScannerUtils

except ImportError as e:
    print str(e)

setproctitle('barcode_scanner')

DEBUG = False

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

        self.full_power_event = threading.Event()  # clear means eco mode on
        self.full_power_event.set()

        self.server_url = url

        # threads
        self.t1 = threading.Thread(target=self.status_thread, name='show_status')
        self.t2 = threading.Thread(target=self.scan_thread, name='scanner')
        self.timer = TimerClass(5)  # TODO set this to much higher # of seconds

        if pi:
            self.led = RGB_LED()

        self.start()

    def start(self):
        """

        :return:
        """
        self.t1.start()  # start status thread
        self.t2.start()  # scanner thread
        self.timer.start()   # timer thread starts

        self.timer.restart()  # TODO should be an initial start not a restart method

        # TODO should not need to have this line
        ScannerUtils.find_process('zbarcam', True)  # kill rogue scanner

        try:
            while True:
                time.sleep(10)
                # checking to see if the timer finished
                if self.timer.done:  # TODO better way to do this instead of bool?
                    self.full_power_event.clear()  # power down camera thread
                    ScannerUtils.find_process('zbarcam', True)
                    self.timer.done = False

                if DEBUG:
                    if not self.full_power_event.is_set():  # eco mode
                        print 'main thread: eco mode'

                    else:
                        print 'main thread: full mode'

                # Setting full_power event will kick things back off

                if self.get_from_server('restart') == 'true':  # ask to see if things should turn back on
                    print 'turning back on'

                    self.full_power_event.set()
                    print 'sending command to shut off restart flag'
                    self.post_to_server('restart/?status=false', 'false')

                    #print self.get_from_server('restart')

                # TODO server polls should be slower,maybe another thread
                time.sleep(3)
                self.post_status()  # send status

        except KeyboardInterrupt:
            print "main thread killed, waiting on threads:"
            self.shutdown()

            print "threads successfully closed"

    def scan_thread(self):
        """
        create a zbar stream subprocess
        grabs output barcode data
        set event if barcode found
        """
        #p = subprocess.Popen(['/usr/bin/zbarcam', '--nodisplay', '/dev/video0'], stdout=subprocess.PIPE)  # run barcode scanner software
        try:
            while self.run_event.is_set():
                time.sleep(3)
                barcode = ''

                # see if zbarcam is already running
                if not ScannerUtils.find_process('zbarcam'):
                    print 'is it turning zbar back on?'
                    p = subprocess.Popen(['/usr/bin/zbarcam', '--nodisplay', '/dev/video0'], stdout=subprocess.PIPE)  # run barcode scanner software

                if self.full_power_event.is_set():

                    print 'scanner: full power'

                    if DEBUG:
                        print'\tscanner waiting on status event to scan again'

                    if not self.status_event.is_set():

                        code = p.stdout.readline()  # thread stuck here waiting for barcode

                        if code == '':  # when zbarcam is killed code == ''
                            code = ':'

                        barcode = code.split(':')[1].rstrip()  # strips out type of barcode and the trailing char

                        # got a barcode reset timer
                        if barcode is not '':
                            if DEBUG:
                                print 'barcode found: %s, reset timer' % barcode
                            self.timer.restart()  # TODO turn this back on

                        post = 'inventory/' + barcode
                        self.post_to_server(post, barcode)  # send barcode to server

                        self.status_event.set()  # valid barcode trigger green light
                        # this should cause the scanner to stop till light has been shown

                else:  # self.full_power_event.is_set():

                    print 'scanner: eco mode'

            else:
                print 'scanner shutdown'
        except Exception as e:
            print e

    def status_thread(self):
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
            time.sleep(2)

            # self.full_power_event.wait()  # dont want to use wait since we want to show a led light always

            if self.full_power_event.is_set():  # full power
                print'status: full power'
                if self.status_event.is_set():  # if barcode is received then return a green
                    if pi:
                        self.led.color(green, 2)
                    if DEBUG:
                        print 'Green led'
                        time.sleep(5)

                    self.status_event.clear()
                else:
                    if pi:  # turn light back to blue
                        self.led.color(blue, 1)
                    if DEBUG:
                        print 'Blue led'
                        time.sleep(5)

            else:  # is not self.full_power_event.is_set():  # TODO make this a slow pulse
                print 'status: eco mode'

                if pi:
                    self.led.color(tuple(x/2 for x in red), 0.5)
                if DEBUG:
                    print 'red led orb'

        else:
            print 'status: shutdown'

    def post_to_server(self, uri, data):
        """

        :param uri:
        :param data:
        :return:
        """
        if self.server_url is not None:
            r = requests.post(self.server_url + uri, data=data)

            #if DEBUG:
            status = r.status_code
            if DEBUG:
                print '\t\t%s' % r.url
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
        try:
            if self.server_url is not None:
                r = requests.get(self.server_url + uri)
                print r.content
                status = r.status_code
                print r.url
                # TODO check response for 200 HTTP ok, 400 bad requests, 500 api issue
                if status == 200:
                    #print 'all good'
                    return r.content
                else:
                    #print status
                    return False
            else:
                print 'cant GET, no server specified'
        except(requests.HTTPError,requests.Timeout) as e:
            print e

    def post_status(self):
        """
        check status of program and return it to the rest api
        """

        count = threading.active_count()

        if DEBUG:
            print '\t\tCurrent # of threads running ' + str(count)

        if count == 4:  # count will be 4 with timer
            status = 'healthy'
        else:  # only the main thread is running
            status = 'critical'

        if not self.full_power_event.is_set():
            status = 'warning'

        post = 'health/scanner/?status=' + status

        self.post_to_server(post, status)

    def shutdown(self):
        """

        :return:
        """
        self.full_power_event.set()  # wakeup any waiting threads so we can kill them
        self.run_event.clear()  # this really should be enough stop threads from running?
        self.timer.kill()  # stops

        ScannerUtils.find_process('zbarcam', True)

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

        self.done = False

        self.length = length  # initial timer amount to be able to reset at same duration
        self.count = length  # current timer amount

    def run(self):
        while not self.timer_finished.is_set():
            time.sleep(.1)  # tiny pause needed to let other threads run
            if not self.timer_paused.is_set():  # not paused
                if self.count > 0:  # still need to count down
                    print self.count
                    self.count -= 1
                    self.timer_paused.wait(1)  # pause a second to act like a timer

                else:  # self.count == 0:
                    print 'timer completed'
                    self.done = True
                    self.stop()

            # this is only needed for debug purposes
            else:  # timer paused
                if self._DEBUG:
                    print 'timer paused'
                self.timer_paused.wait()

    def kill(self):
        self.timer_finished.set()
        print 'timer shutdown'

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
    scan = Scanner('http://localhost:5000/')  #'http://localhost:5000/')  # 'http://10.253.85.225:5000/'

