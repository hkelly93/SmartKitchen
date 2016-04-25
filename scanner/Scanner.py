# TODO could use socket IO to accept commands from the API instead of useing a file as a in-between
try:
    import os
    import time
    import subprocess
    import threading
    import Queue
    from setproctitle import setproctitle
    import requests
    import hashlib
    import ScannerUtils

except ImportError as e:
    print str(e)

setproctitle('barcode_scanner')

TOKEN = hashlib.sha256('LEN2M1s0d2Q8ZD9FfTptJg==').hexdigest()
DEBUG = True
scanoff = False

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
        self.status_event = threading.Event()  # set when a barcode is received
        self.status_event.set()

        self.full_power_event = threading.Event()  # clear means eco mode on
        self.full_power_event.set()

        # share data between threads
        self.status_queue = Queue.Queue()  # FIFO
        self.scanner_queue = Queue.Queue()

        # threads
        self.status_thread = StatusThread([self.status_event, self.full_power_event])
        self.scanner_tread = ScannerThread([self.status_event, self.full_power_event], self.scanner_queue)
        self.timer = TimerThread(60, self.full_power_event)  # TODO set this to much higher # of seconds

        # local vars
        self.server_url = url

        self.start()

    def start(self):
        self.status_thread.start()  # start status thread

        if not scanoff:
            ScannerUtils.find_process('zbarcam', True)  # kill rogue scanner
            self.scanner_tread.start()  # scanner thread

        self.timer.start()   # timer thread starts

        if DEBUG:
            print 'main: starting up'
        try:
            while True:
                time.sleep(1)

                # a finished timer will put system into ECO Mode

                if self.timer.done:
                    print 'after timer done'
                    self.full_power_event.clear()  # ECO Mode

                    # makes sure it wont restart unless told to
                    self.post_to_server('restart/?status=false', 'false')
                    self.timer.done = False

                    #if not scanoff:
                        #self.scanner_tread.zbar.terminate()
                        #ScannerUtils.find_process('zbarcam', True)  # TODO a nicer way to do this?

                if not self.full_power_event.is_set():
                    if DEBUG:
                        print 'main thread: eco mode'

                    time.sleep(2)  # slow down api calls
                    self.restart()  # eco mode check for restart from UI

                else:  # full power mode
                    if DEBUG:
                        print 'main thread: full mode'

                    # barcode received
                    if not self.scanner_queue.empty():

                        barcode = self.scanner_queue.get()
                        print 'getting item out of queue %s' % barcode
                        #self.scanner_queue.task_done()

                        print 'after get from queue'
                        if barcode is not '':
                            print 'barcode found, restarting timer'
                            #self.timer.restart()

                            # send barcode to server
                            uri = '/inventory/' + barcode
                            self.post_to_server(uri, barcode)

                            #self.timer.restart()  # timer needs to be restarted to keep full_power active

                            #self.status_event.set()  # tell status thread and scanner that we got a barcode
                            time.sleep(.1)

                #self.post_status()  # send status
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

            self.full_power_event.set()  # this wakes up every thread but timer
            self.timer.reset(True)  # need to restart timer
            time.sleep(.1)
            # print 'sending command to shut off restart flag'
            self.post_to_server('restart/?status=false', 'false')

    def post_to_server(self, uri, data):
        """

        :param uri:
        :param data:
        :return:
        """
        token = '?token=' + TOKEN
        try:
            if self.server_url is not None:
                r = requests.post(self.server_url + uri , data=data + token)

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
                #print r.content
                status = r.status_code
                #print r.url
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

        if DEBUG:
            print '\t\tCurrent # of threads running ' + str(count)
            print threading.enumerate()
        if self.full_power_event.is_set():
            if count == 4:  # 4 with zbar
                status = 'healthy'
            else:  # only the main thread is running
                status = 'critical'

        else:
            if count == 4:
                status = 'warning'
            else:
                status = 'critical'

        post = 'health/scanner/?status=' + status

        self.post_to_server(post, status)

    def shutdown(self):
        """

        :return:
        """

        if not scanoff:
            self.scanner_tread.kill()

        self.timer.kill()

        self.status_thread.kill()

        # threads could be in eco or full mode
        self.full_power_event.set()  # wakes up timer and scanner functions if in eco mode
        time.sleep(.1)

        try:
            # cleaning up threads will throw error if they are already killed
            self.status_thread.join()
            print 'status_thread joined'

            self.timer.join()
            print 'timer_thread joined'

            if not scanoff:
                # make sure zbar is dead before attempting to join
                #ScannerUtils.find_process('zbarcam', True)
                self.scanner_tread.join()  #TODO scanner thread getting stuck
                print 'scanner_tread joined'

        except RuntimeError as e:
            print e


class StatusThread(threading.Thread):
    global pi

    def __init__(self, events, queue=''):
        threading.Thread.__init__(self)
        self.name = 'status'
        self._DEBUG = True
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

        red = (100, 0, 0)  # TODO if scanner thread has terminated
        green = (0, 100, 0)
        blue = (0, 0, 100)

        if self._DEBUG:
            print '\t\tBlue led'

        try:
            while not self.status_finished.is_set():
                time.sleep(1)
                if self.full_power_event.is_set():  # full power
                    if pi:  # turn light back to blue
                        self.led.color(blue)
                    if self._DEBUG:
                        print'\tstatus: full power'

                    if not self.status_event.is_set():  # scanner thread has set this to clear if barcode returned
                        if pi:
                            self.led.color(green, 3)
                            self.led.color(blue)
                        if self._DEBUG:
                            print '\t\tGreen led'

                        print 'status sets status event'
                        #self.status_event.set()  # wakes up scanner
                        time.sleep(.1)

                    else:
                        if self._DEBUG:
                            print '\t\tBlue led'

                else:  # is not self.full_power_event.is_set()
                    if self._DEBUG:
                        print '\tstatus: eco mode'

                    if pi:
                        for i in range(0, 720, 5):  # makes light orb
                            self.led.color((0, 0, self.led.PosSinWave(50, i, 2)), .1)

                    elif self._DEBUG:
                        print '\t\tblue led orb'
            else:
                print '\tstatus: shutdown'

        except Queue.Empty as e:
            if self._DEBUG:
                print '\t\tqueue is empty'
            pass

        except Exception as e:
            print e.message

    def kill(self):
        print '\tstatus: killed'
        if pi:  # shut off led
            self.led.cleanup()
        self.status_event.set()  # make sure scanner is not waiting for this event
        self.status_finished.set()  # this will kill main loop
        time.sleep(.1)


class ScannerThread(threading.Thread):
    def __init__(self, events, queue):
        threading.Thread.__init__(self)
        self.name = 'scanner'
        self._DEBUG = True

        self.queue = queue
        self.zbar = None

        # Events
        self.status_event = events[0]
        self.full_power_event = events[1]
        self.scanner_finished = threading.Event()  # set means that we should kill thread

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

                    # startup zbarcam if not currently running
                    if not ScannerUtils.find_process('zbarcam'):
                        if self._DEBUG:
                            print '\t\tstarting zbarcam'
                        if pi:
                            self.zbar = subprocess.Popen(['/usr/bin/zbarcam', '--nodisplay', '/dev/video0'], stdout=subprocess.PIPE)
                        else:
                            self.zbar = subprocess.Popen(['/usr/bin/zbarcam', '/dev/video0'], stdout=subprocess.PIPE)

                        # thread pauses here waiting for barcode to be sent
                    else:
                        if self._DEBUG:
                            print '\t\talready exists'

                    # if not self.pause_event.is_set():  # wait to grab another scan
                    if self._DEBUG:
                        print '\t\tready to get next barcode'

                    code = self.zbar.stdout.readline()  # thread stuck here waiting for barcode
                    '''
                    code = self.zbar.communicate()
                    print type(code)

                    if code[0] == '':  # when zbarcam is killed code == ''
                        code = (':', '')

                    barcode = code[0].split(':')[1].rstrip()  # strips out type of barcode and the trailing char

                    '''
                    if code == '': # need this if zbarcam is killed
                        code = ':'

                    barcode = code.split(':')[1]
                    #print type(barcode)

                    # got a barcode reset timer
                    if barcode is not '':
                        #self.zbar.terminate()
                        print 'still running'
                        if self._DEBUG:
                            print '\t\tbarcode found: %s' % barcode

                        self.queue.put(barcode)  # item in queue will allow main thread to post item to server
                        self.queue.task_done()
                        #self.status_event.clear()  # will trigger green light in status thread

                        if self._DEBUG:
                            print 'scanner pausing and triggering green light'
                        time.sleep(.1)
                        #self.zbar.terminate()
                        #self.status_event.wait()  # waits till status sets this event so we have a break in scanning

                    else:
                        if self._DEBUG:
                            print '\t\tinvalid barcode'
                        pass

                else:
                    if self._DEBUG:
                        print '\tscanner: eco mode'
                        #self.zbar.kill()
                        #ScannerUtils.find_process('zbarcam', True)  # kill zbarcam
                    #self.full_power_event.wait()

            else:  # scanner_finished event is set
                #ScannerUtils.find_process('zbarcam', True)  # kill zbarcam
                print '\tscanner: shutting down'

        except Exception as e:
            print e

    def kill(self):
        if self._DEBUG:
            print '\t\tscanner: killed'

        self.scanner_finished.set()  # this will kill main loop

        time.sleep(.1)

        self.status_event.set()

        print 'trying to terminate zbar'
        self.zbar.terminate()


class TimerThread(threading.Thread):
    """

    """
    def __init__(self, length, event=''):
        threading.Thread.__init__(self)
        self._DEBUG = True

        # Events start clear
        self.full_power_event = event
        self.timer_finished = threading.Event()   # clear means keep running
        self.timer_paused = threading.Event()  # clear means timer is not paused
        # self.timer_paused.set()

        self.done = False

        self.length = length  # initial timer amount to be able to reset at same duration
        self.count = length  # current timer amount

    def run(self):
        while not self.timer_finished.is_set():
            time.sleep(.1)  # tiny pause needed to let other threads run

            # full power
            if self.full_power_event.is_set():
                if not self.timer_paused.is_set():  # not paused (clear) # self.full_power_event.is_set() and not
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
                    self.stop()

            else:
                print 'eco mode but timer not paused'
                self.stop()
                # self.full_power_event.wait()

        else:
            print '\ttimer: shutdown'

    def kill(self):
        print '\ttimer: killed'
        self.timer_finished.set()
        time.sleep(.1)
        self.timer_paused.set()  # make sure thread is not waiting on this event
        time.sleep(.1)

    def stop(self):
        if not self.timer_paused.is_set():  # not paused (clear)
            if self._DEBUG:
                print 'pause and reset'
            self.pause()
            self.reset()
        else:  # already paused
            if self._DEBUG:
                print 'already paused just reset'
            self.reset()

        self.timer_paused.clear()
        self.timer_paused.wait()  # needs to be clear to allow wait functionality

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

        if restart:
            if self._DEBUG:
                print '\trestarting timer with %d seconds' % self.count
            self.resume()

    def pause(self):  # pauses timer until event is flagged true
        if not self.timer_paused.is_set():  # if not paused (clear)
            self.timer_paused.set()  # will pause on next loop

        else:
            if self._DEBUG:
                print '\talready paused'

    def resume(self):
        if self.timer_paused.is_set():  # is paused (set)
            self.timer_paused.clear()

        else:
            if self._DEBUG:
                print '\talready running'

if __name__ == "__main__":
    scan = Scanner('http://localhost:5000/')  #'http://localhost:5000/')  # 'http://10.253.85.225:5000/'

