# TODO could use socket IO to accept commands from the API instead of useing a file as a in-between
try:
    import os
    import time
    import subprocess
    import threading
    import Queue
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
        # Events
        self.status_event = threading.Event()  # true when a barcode is received
        self.status_event.set()

        self.full_power_event = threading.Event()  # clear means eco mode on
        self.full_power_event.set()

        # share data between threads
        self.status_queue = Queue.Queue()  # FIFO
        self.scanner_queue = Queue.Queue()

        # threads
        self.t1 = StatusThread([self.status_event, self.full_power_event])
        self.t2 = ScannerThread([self.status_event, self.full_power_event], self.scanner_queue)
        self.timer = TimerThread(10, self.full_power_event)  # TODO set this to much higher # of seconds

        # local vars
        self.server_url = url

        self.start()

    def start(self):
        self.t1.start()  # start status thread
        self.t2.start()  # scanner thread
        self.timer.start()   # timer thread starts

        # self.timer.restart()  # by default the timer starts paused

        ScannerUtils.find_process('zbarcam', True)  # kill rogue scanner
        if DEBUG:
            print 'main: starting up'
        try:
            while True:
                time.sleep(5)

                if DEBUG:
                    if not self.full_power_event.is_set():  # eco mode
                        print 'main thread: eco mode'

                    else:
                        print 'main thread: full mode'

                # a finished timer will put system into ECO Mode
                if self.timer.done:  # TODO better way to do this instead of bool?
                    self.full_power_event.clear()  # ECO Mode
                    self.post_to_server('restart/?status=false', 'false')
                    self.timer.done = False

                    ScannerUtils.find_process('zbarcam', True)  # TODO a nicer way to do this?

                if not self.full_power_event.is_set():
                    print 'eco mode is on'
                    # TODO make sure zbar is dead

                    time.sleep(10)  # slow down api calls
                    self.restart()  # eco mode check for restart from UI

                else:  # full power mode
                    # barcode received
                    if not self.scanner_queue.empty():
                        print 'getting item out of queue' + self.scanner_queue.get_nowait()
                        barcode = self.scanner_queue.get_nowait()

                        # send barcode to server
                        uri = '/inventory/' + barcode
                        self.post_to_server(uri, barcode)

                        self.timer.restart()  # timer needs to be restarted to keep full_power active

                        self.status_event.clear()  # tell status thread that we got a barcode

                # TODO server polls should be slower,maybe another thread
                self.post_status()  # send status

        except Queue.Empty as e:
            if DEBUG:
                print e
            pass

        except KeyboardInterrupt as e:
            print "main thread signaled for kill, waiting on threads:"
            self.shutdown()

            print "threads successfully closed"

        except Exception as e:
            print e

    def restart(self):
        if self.get_from_server('restart/') == 'true':  # ask to see if things should turn back on

            print 'main: restarting threads'

            self.full_power_event.set()
            #print 'sending command to shut off restart flag'
            self.post_to_server('restart/?status=false', 'false')

            # TODO change timer to use full_power event instead?
            self.timer.timer_paused.set()  # need to restart timer

            #print 'reset is now set to: ' + self.get_from_server('restart/')

    def post_to_server(self, uri, data):
        """

        :param uri:
        :param data:
        :return:
        """
        try:
            if self.server_url is not None:
                r = requests.post(self.server_url + uri, data=data)

                #if DEBUG:
                status = r.status_code
                if DEBUG:
                    print '\t\t%s%s' % (r.url, uri)
                # TODO check response for 200 HTTP ok, 400 bad requests, 500 api issue
                if status == 200:
                    #print 'all good'
                    return True
                else:
                    #print status
                    return False
            else:
                print 'cant POST no server specified'
        except(requests.HTTPError, requests.Timeout, requests.exceptions.ConnectionError) as e:
            message = 'Connection to {0} failed. \n {1}'
            print message.format(self.server_url, e)

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
        except(requests.HTTPError, requests.Timeout, requests.exceptions.ConnectionError) as e:
            message = 'Connection to {0} failed. \n {1}'
            print message.format(self.server_url, e)

    def post_status(self):
        """
        check status of program and return it to the rest api
        """

        count = threading.active_count()

        #if DEBUG:
        print '\t\tCurrent # of threads running ' + str(count)

        if count == 4:  # count will be 4 with timer
            status = 'healthy'
        else:  # only the main thread is running
            status = 'critical'

        if not self.full_power_event.is_set():
            status = 'warning'

        print status
        post = 'health/scanner/?status=' + status

        self.post_to_server(post, status)

    def shutdown(self):
        """

        :return:
        """
        self.full_power_event.set()  # wakeup any waiting threads so we can kill them

        #run_event.clear()  # this really should be enough stop threads from running?

        self.timer.kill()
        self.t1.kill()
        self.t2.kill()

        try:
            # cleanup threads will throw error if they are already killed
            self.t1.join()
            self.t2.join()
            self.timer.join()
        except RuntimeError as e:
            pass


class StatusThread(threading.Thread):
    global pi

    def __init__(self, events, queue=''):
        threading.Thread.__init__(self)
        self.name = 'status'
        self._DEBUG = False
        self.queue = queue

        # Events
        self.status_finished = threading.Event()  # set means that we should kill thread
        self.status_event = events[0]
        self.full_power_event = events[1]

        if pi:
            self.led = RGB_LED()

    def run(self):
        """
        displays program status on hardware
        normally should be displaying a blue light
        triggers green light for 3 seconds only if barcode is found in scan thread
        triggers pulsing red light if in eco mode
        """
        if self._DEBUG:
            print '\tstatus: starting up'
        red = (100, 0, 0)
        green = (0, 100, 0)
        blue = (0, 0, 100)

        try:
            while not self.status_finished.is_set():
                time.sleep(1)
                if self._DEBUG:
                    print '\tstatus: running'

                if self.full_power_event.is_set():  # full power
                    print'\tstatus: full power'

                    if DEBUG:
                        print '\t\tBlue led'

                    if pi:  # turn light back to blue
                        self.led.color(blue)

                    # TODO should this be clear so that we can have the other thread wait till led is shown????
                    if not self.status_event.is_set():  # if barcode is received then return a green
                        if pi:
                            self.led.color(green, 3)
                            self.led.color(blue)
                        if DEBUG:
                            print '\t\tGreen led'

                        self.status_event.set()  # triggers event so scanner knows it can scan again

                else:  # is not self.full_power_event.is_set():  # TODO make this a slow pulse
                    if self._DEBUG:
                        print '\tstatus: eco mode'

                    if pi:
                        self.led.color(tuple(x/2 for x in red), 0.5)

                    if DEBUG:
                        print '\t\tred led orb'
            else:
                print '\tstatus: shutdown'

        except Queue.Empty as e:
            if self._DEBUG:
                print '\tqueue is empty'
            pass

        except Exception as e:
            print e.message

    def kill(self):
        if pi:  # shut off led
            self.led.cleanup()
        self.status_event.set()  # make sure this is not paused
        self.status_finished.set()  # this will kill main loop


class ScannerThread(threading.Thread):
    def __init__(self, events, queue):
        threading.Thread.__init__(self)
        self.name = 'scanner'
        self._DEBUG = True

        self.queue = queue

        # Events
        self.status_event = events[0]
        self.full_power_event = events[1]
        self.scanner_finished = threading.Event()  # set means that we should kill thread
        # self.pause_event = threading.Event()

    def run(self):
        if self._DEBUG:
            print '\tscanner: startup'
        try:
            while not self.scanner_finished.is_set():  # keep running unless set
                if self._DEBUG:
                    print '\tscanner: running'
                time.sleep(1)

                if self.full_power_event.is_set():
                    if self._DEBUG:
                        print '\tscanner: full power'
                    # see if zbarcam is already running
                    if not ScannerUtils.find_process('zbarcam'):
                        if self._DEBUG:
                            print '\t\tstarting zbarcam'
                        # run barcode scanner software
                        p = subprocess.Popen(['/usr/bin/zbarcam', '--nodisplay', '/dev/video0'], stdout=subprocess.PIPE)
                        # thread gets stuck here waiting for barcode to be sent
                    else:
                        if self._DEBUG:
                            print '\t\talready exists'

                    # if not self.pause_event.is_set():  # wait to grab another scan
                    if self._DEBUG:
                        print '\t\tready to get next barcode'

                    code = p.stdout.readline()  # thread stuck here waiting for barcode

                    # hacky way to make code.split not error out
                    if code == '':  # when zbarcam is killed code == ''
                        code = ':'

                    barcode = code.split(':')[1].rstrip()  # strips out type of barcode and the trailing char

                    # got a barcode reset timer
                    if barcode is not '':
                        if self._DEBUG:
                            print '\t\tbarcode found: %s' % barcode

                        self.queue.put(barcode) # item in queue will allow main thread to post item to server

                        self.status_event.clear()  # will trigger green light in status thread

                        # TODO test to see if you dont put a time out if it will ever go into eco-mode
                        self.status_event.wait(5)  # waits till status sets this event so we have a break in scanning
                        #self.full_power_event.wait()
                    else:
                        if self._DEBUG:
                            print '\t\tinvalid barcode'
                        pass
                else:
                    if self._DEBUG:
                        print '\tscanner: eco mode'
                    self.full_power_event.wait()

            else:  # scanner_finished event is set
                # cleanup
                ScannerUtils.find_process('zbarcam', True)  # kill zbarcam
                print '\tscanner: shutting down'

        except subprocess.CalledProcessError as e:
            # something wrong with trying to start process
            print e.output
    '''
    def eco_mode(self):
        if self._DEBUG:
            print '\tscanner: eco mode'
        ScannerUtils.find_process('zbarcam', True)  # kill zbarcam
        self.full_power_event.wait()  # should pause here until event is set
    '''
    def kill(self):
        if self._DEBUG:
            print '\t\tkill sent to scanner'
        # self.pause_event.set()  # make sure this is not paused
        self.scanner_finished.set()  # this will kill main loop


class TimerThread(threading.Thread):
    """

    """
    def __init__(self, length, event=''):
        threading.Thread.__init__(self)
        self._DEBUG = False
        # Events start clear
        self.full_power_event = event
        self.timer_finished = threading.Event()   # clear means keep running
        self.timer_paused = threading.Event()  # clear means timer is not paused
        self.timer_paused.set()

        self.done = False

        self.length = length  # initial timer amount to be able to reset at same duration
        self.count = length  # current timer amount

    def run(self):
        while not self.timer_finished.is_set():
            time.sleep(1)  # tiny pause needed to let other threads run

            # if self.timer_paused.is_set():
            if self.full_power_event.is_set() and self.timer_paused.is_set():  # not paused (set)
                if self._DEBUG:
                    print '\ttimer not paused'

                if self.count > 0:  # still need to count down
                    #if self._DEBUG:
                    print self.count
                    self.count -= 1
                    self.timer_paused.wait(1)  # pause a second to act like a timer

                else:  # self.count == 0:
                    if self._DEBUG:
                        print '\ttimer completed'
                    self.done = True
                    self.stop()

            else:  # timer paused (clear)
                if self._DEBUG:
                    print '\ttimer paused'
                self.timer_paused.clear()  # need to clear to allow wait functionality
                self.full_power_event.wait()  # waits till timer event is set
                #self.full_power_event

    def kill(self):
        self.timer_paused.set()
        self.timer_finished.set()
        time.sleep(1)
        print '\ttimer shutdown'

    def stop(self):
        if self.timer_paused.is_set():  # not paused (set)
            self.pause()
            self.reset()
        else:  # already paused
            self.reset()

    def restart(self):
        if self.timer_paused.is_set():  # not paused (set)
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
            print '\trest timer with %d seconds' % self.count

        if restart:
            self.resume()

    def pause(self):  # pauses timer until event is flagged true
        if self.timer_paused.is_set():  # if not paused (set)
            self.timer_paused.clear()  # will pause on next loop

        else:
            if self._DEBUG:
                print '\talready paused'

    def resume(self):
        if not self.timer_paused.is_set():  # is paused (clear)
            self.timer_paused.set()

        else:
            if self._DEBUG:
                print '\talready running'

if __name__ == "__main__":
    scan = Scanner('http://localhost:5000/')  #'http://localhost:5000/')  # 'http://10.253.85.225:5000/'

