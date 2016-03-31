import os
import threading
import requests
import time

run_event = threading.Event() # if this is False then the sub threads will terminate
run_event.set()

status_event = threading.Event()  # used to control current running thread
status_event.set()

eco_event = threading.Event()  # False means both threads should be on
eco_event.clear()


def timer():
    """
    create a timer to shut down threads when not used for a long time
    after x seconds set the run_event flag to False

    """
    run_event.clear()
    eco_event.set()  # is this needed?
    t1.join()
    t2.join()



def POST(barcode): # TODO make this into a generic function
    post = 'http://127.0.0.1:5000/' + 'addInventory/' + barcode + '/'
    r = requests.post(post, data=barcode)
    status = r.status_code

    print r.url
    # check response for 200 HTTP ok, 400 bad request, 500 api issue
    if status == 200:
        print 'all good'
        #return True
    else:
        print status
        #return False


def scan():
    """
    create a zbar stream subprocess
    grab outputed barcode data
    set event if barcode found
    """

    p = os.popen('/usr/bin/zbarcam', 'r')  # run barcode scanner software

    while run_event.is_set():
        time.sleep(.1)  # slight pause is needed to allow other threads to show
        #print 'scanner waiting on status event to scan again'
        while status_event.is_set():
            #print "scan thread running"
            code = p.readline()  # should only get the latest line from barcode scanner
            print 'Got barcode:', code
            barcode = code.split(':')[1].rstrip()  # strips out type of barcode and the trailing char
            #barcode = barcode.rstrip()
            #print "|" + barcode + "|"

            POST(barcode)  # send barcode to server

            status_event.clear()  # valid barcode trigger green light
            # this should cause the scanner to stop till light has been shown


def show_status():
    """
    displays program status on hardware
    should always be running
    triggers green light only if barcode is found in scan thread
    TODO triggers red light if scanner thread is no up in running
    """
    while run_event.is_set():  # not run_event.is_set:
        # print "status update here"
        if not status_event.is_set():  # if barcode is received then return a green
            print 'green light whould stay on for 3 secs here'
            time.sleep(3)
            status_event.set()

        else:  # waiting on a barcode
            print 'yellow light'

        # TODO put another if statement to make red light flash if scanner thread is not active
        time.sleep(2)  # dont need to update the lights too often
    '''
    # TODO this doesnt die correctly if the parent thread is killed
    if not run_event.is_set():  # scanner must be down
        # TODO should try and setup something to try and restart scanner thread
        while True:
            print 'RED LIGHT flashes'
            time.sleep(.5)
    '''

if __name__ == "__main__":

    t1 = threading.Thread(target=show_status, name='show_status')  # , args=(i,))
    t2 = threading.Thread(target=scan, name='scanner')

    t2.start()
    t1.start()

    #t = threading.Timer(10, timer())  # timer object for setting eco mode
    #t.start()

    try:
        while True:
            print 'main thread running'
            time.sleep(3)  # update website status but not too often

            # print threading.active_count()  # will return 3 if all good
            if threading.active_count() == 3:
                status = 'healthy'
            else:  # 1 or 2 threads running
                status = 'warning'

                # power saver mode on? no? then don restart threads that are down
                if not eco_event.is_set():
                    # check what threads are not running and recreate them
                    if not t1.is_alive():
                        print "status thread dead, restarting"
                        t1 = threading.Thread(target=show_status, name='show_status')  # , args=(i,))
                        t1.start()
                    if not t2.is_alive():
                        print "scanner thread is dead, restarting"
                        t2 = threading.Thread(target=scan, name='scanner')
                        t2.start()


            # TODO combine this with POST method
            post = 'http://127.0.0.1:5000/' + 'setScannerHealth/' + status + '/'
            r = requests.post(post, data=status)
            # status = r.status_code
            # critical status should show if this code was not running

            # TODO check if threads are active if not re-create new ones
            # find a way to shut down scanner thread only but leave others active for power saving


    except KeyboardInterrupt:
        print "main thread killed"
        run_event.clear()
        t1.join()
        t2.join()
        print "threads successfully closed"






