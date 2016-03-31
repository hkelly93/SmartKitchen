import os
import threading
import requests
import time

run_event = threading.Event()
run_event.set()  # True means that the parent thread is still running

status_event = threading.Event()
run_event.clear()  #defaults to not haveing a valid barcode

def post_barcode(barcode='123456789'):
    post = 'http://127.0.0.1:5000/' + 'addInventory/' + barcode + '/'
    r = requests.post(post, data=barcode)
    status = r.status_code

    print r.url
    # check respose for 200 HTTP ok, 400 bad request, 500 api issue
    if status == 200:
        print 'all good'
        return True
    else:
        print status
        return False


# create status thread
class StatusThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        # if scanner is down return a yellow
        # if scanner is up then return a green
        while run_event.is_set():
            time.sleep(5)
            print "status update here"


def status():
    # if scanner is down return a yellow
    # if scanner is up then return a green
    while run_event.is_set():
            time.sleep(5)
            print "status update here"

if __name__ == "__main__":
    #thread1 = StatusThread("Scanner")
    #thread1.start()

    t = threading.Thread(target=status)  # , args=(i,))
    t.start()

    # could do a second thread that runs the scanner?
    try:
        p = os.popen('/usr/bin/zbarcam', 'r')
        while True:
            time.sleep(3) # only get barcode every 3 seconds
            print "main thread running"
            code = p.readline()
            print 'Got barcode:', code
            barcode = code.split(':')[1]  # strips out type of barcode
            barcode = barcode.rstrip()
            print "|" + barcode + "|"
            status_event.set()  # let threads know we got a barcode
            post_barcode(barcode)

    except KeyboardInterrupt:
        print "main thread killed"
        run_event.clear()
        #thread1.join()
        t.join()
        print "threads successfully closed"






