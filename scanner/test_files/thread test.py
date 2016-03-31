#!/usr/bin/python

import threading

from scanner.test_files import scanner

barcode = False

c = threading.Condition() # this probably should be an event instead


class ScanThread(threading.Thread):
    global barcode, c

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

        # create scanner
        self.scanner = scanner.scanner.Scanner()

    def run(self):
        global barcode
        #print "Starting " + self.name

        while True:
            c.acquire()
            # waits for zbar to give it a barcode
            #status = raw_input("barcode:") # raw input locks up thread
            barcode = self.scanner.get_barcode()
            print barcode
            '''
            if not barcode == '':  # only spits back info if barcode scanned so anything should count for now
                print 'received valid scan'
                post = 'http://127.0.0.1:5000/addInventory/' + barcode + '/'
                r = requests.post(post)
                print r.status_code()  # check respose for 200 HTTP ok, 400 bad request, 500 api issue
                # anything but 404 we can change network status
                if r == 200:
                    print'all good'
                elif r == 400:
                    #TODO make function for post, uri then data to put
                    print 'bad request'
                # 404 call didnt go through
            '''
            else:
                #print status
                print 'waiting on valid scan'
            c.notify_all()
            c.wait()
        c.release()
        #print "Exiting " + self.name


class StatusThread(threading.Thread):
    global barcode, c

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        global barcode
        #print "Starting " + self.name

        while True:
            c.acquire()  # get condition(lock)
            # should replace this with a function
            show_status()
            c.notify_all()  # ready for next barcode
            c.wait()
        c.release()
        #print "Exiting " + self.name


def show_status():
    global barcode
    if not barcode == '':
        print 'green led'
    else:
        print 'yellow led'

# Create new threads
thread1 = ScanThread(1, "Scanner", 1)
#thread2 = StatusThread(2, "Status", 2)

# Start new Threads
#thread1.setDaemon(True)
#thread2.setDaemon(True)
try:
    thread1.start()
    #thread2.start()
except KeyboardInterrupt:
    pass

# print "Exiting Main Thread"