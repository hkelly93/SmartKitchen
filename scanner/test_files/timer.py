import threading
import time

DEBUG = True


class TimerClass(threading.Thread):
    def __init__(self, length):
        threading.Thread.__init__(self)

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
        if DEBUG:
            print 'rest timer with %d seconds' % self.count

        if restart:
            self.resume()

    def pause(self):  # pauses timer until event is flagged true
        if not self.timer_paused.is_set():  # if not paused
            self.timer_paused.set()  # will pause on next loop
        else:
            print 'already paused'

    def resume(self):
        if self.timer_paused.is_set():  # is paused
            self.timer_paused.clear()
        else:
            print 'already running'


class ScannerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # starts off with thread running
        # need to start the timer itself

        time.sleep(2)
        print '\ttimer restarted'
        tmr.restart()

        time.sleep(2)
        print '\ttimer stopped'
        tmr.stop()

        time.sleep(2)
        print '\ttimer restarted'
        tmr.restart()

        time.sleep(2)
        print '\ttimer resumed'
        tmr.pause()
        time.sleep(2)
        tmr.resume()



tmr = TimerClass(10)

scn = ScannerClass()
tmr.start()
scn.start()

try:
    while True:

        time.sleep(5)
        print 'main loop'

except KeyboardInterrupt:
    tmr.kill()
    tmr.join()
    scn.join()

