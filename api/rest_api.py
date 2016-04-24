import datetime
import json
import uuid

from flask import Flask, jsonify, request
from lockfile import LockFile

from util.RestUtils import RestUtils
from messages import Messages
from flask.ext.cors import CORS

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'UfrWq8uk7bRvKewY9VwKX7FN'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)


@app.route('/health/<string:part>/', methods=['GET', 'POST'])
def health(part):
    lock = None
    try:
        lock = LockFile('json/health.json')
        lock.acquire()

        # TODO need to check if scanner is actually on, file is not enough
        with open('json/health.json', 'r') as json_file:
            data = json.load(json_file, encoding='utf-8')

            #status = request.args.get('status', type=str)

            if request.method == 'POST':
                status = request.args.get('status', type=str)
                data[part] = status

                # print status
                with open('json/health.json', 'w') as json_file:
                    json_file.write(json.dumps(data))
                    lock.release()
                    return ''

            if request.method == 'GET':
                if part == 'scanner':  # check if process is running
                    running = RestUtils.find_process('barcode_scanner', False)

                    if not running:
                        data[part] = 'critical'
                        with open('json/health.json', 'w') as json_file:
                            json_file.write(json.dumps(data))
                lock.release()
                return data[part]

    except IOError:
        if lock != None:
            lock.release()
        return Messages.inventoryNotFound()


@app.route('/restart/', methods=['GET', 'POST'])
def restart():  # this really could be health
    lock = None
    try:
        lock = LockFile('json/health.json', 'r')
        lock.acquire()
        with open('json/health.json', 'r') as json_file:

            data = json.load(json_file, encoding='utf-8')

            if request.method == 'POST':
                status = request.args.get('status', type=str)

                if status is None:
                    print 'no status given, defaults to true'
                    status = 'true'

                data['restart'] = status

                with open('json/health.json', 'w') as json_file:
                    json_file.write(json.dumps(data))
                    lock.release()
                    return 'restart set to %s' % status
            if request.method == 'GET':
                lock.release()
                return data['restart']

    except IOError:
        if lock != None:
            lock.release()
        return Messages.inventoryNotFound()


@app.route('/inventory/', methods=['GET'])
def get_inventory():
    """
    TODO loop through inventory to make sure uuid of every item is unique
    only send invenotory if all unique
    """
    lock = None
    try:
        lock = LockFile('json/inventory.json')
        lock.acquire()
        with open('json/inventory.json', 'r') as json_file:
            data = json.load(json_file)  # this will throw correct errors
            lock.release()
            return json.dumps(data)

    except IOError:
        if lock != None:
            lock.release()
        return Messages.inventoryNotFound()


@app.route('/inventory/<string:uuid>', methods=['DELETE', 'GET', 'POST', 'PUT'])
def inventory(uuid):
    """
    DELETE will remove first item with given barcode from inventory

    GET will return first item with this barcode in inventory

    POST will add to inventory
        will increment quantity of pre existing items
    :param uuid: string representation of uuid
    :param days_till_expire: defaults to None which will set it 30 days from todays date
    :return:

    :usage: http://localhost:5000/inventory/1e4658dc-03d5-11e6-b402-7831c1d2d04e?expire=30
    """
    lock = LockFile('json/inventory.json')
    if request.method == 'DELETE':
        try:
            lock.acquire()
            with open('json/inventory.json', 'r') as json_file:
                data = json.load(json_file, encoding='utf-8')  # Get the current inventory.
                json_file.close()
            lock.release()

            index = RestUtils.find_elem(data, 'uuid', uuid)

            if index is not None:
                del data[index]
                lock.acquire()
                with open('json/inventory.json', 'w+') as json_file:
                    json_file.write(json.dumps(data))
                    json_file.close()
                lock.release()
            else:
                print 'nothing to delete'

            return ''  # TODO should tell you if it actually deleted something?

        except (IOError, KeyError):
            if lock != None:
                lock.release()
            print "file doesnt exist or keyerror"

    if request.method == 'GET':
        try:
            lock.acquire()
            with open('json/inventory.json', 'r') as json_file:
                data = json.load(json_file, encoding='utf-8')
                json_file.close()
                index = RestUtils.find_elem(data, 'uuid', uuid)
                if index is not None:
                    lock.release()
                    return jsonify(data[index])
                else:
                    lock.release()
                    return jsonify({})  # TODO what should this return if item doesnt exist?
        except IOError:
            if lock != None:
                lock.release()
            Messages.inventoryNotFound()

    if request.method == 'POST':
        expiration = request.args.get('expire', type=int)

        added_date = datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S")
        expire_date = RestUtils.set_expiration(expiration)

        # TODO add some sort of filelock
        try:
            lock.acquire()
            with open('json/inventory.json', 'r') as json_file:
                data = json.load(json_file, encoding='utf-8')
                json_file.close()
            lock.release()

            barcode = uuid  # thi is needed to not break pre-existing method calls from scanner

            d = {u'barcode': unicode(barcode),
                 u'added': unicode(added_date),
                 u'expiration': unicode(expire_date),
                 u'name': "",
                 u'uuid': unicode(uuid.uuid1())}  # generates unique id for help with deleting items

            data.append(d)

            # open up file again to write to it
            lock.acquire()
            with open('json/inventory.json', 'w+') as json_file:
                json_file.write(json.dumps(data, encoding='utf-8'))
                json_file.close()
            lock.release()

        except (IOError, KeyError) as e:
            # TODO exception error here

            if lock != None:
                lock.release()

            print e

        if lock != None:
            lock.release()

        return ''  # should this really return the whole dict?

    if request.method == 'PUT':
        try:
            expire_date = request.args.get('expires', type=int)
            name = request.args.get('name', type=str)
            date = RestUtils.set_expiration(expire_date)
            lock.acquire()
            with open('json/inventory.json', 'r') as json_file:
                data = json.load(json_file, encoding='utf-8')  # Get the current inventory.
                json_file.close()
            lock.release()

            index = RestUtils.find_elem(data, 'uuid', uuid)

            if index is not None:
                data[index]['expirationdate'] = unicode(date)
                data[index]['name'] = unicode(name)
                lock.acquire()
                with open('json/inventory.json', 'w+') as json_file:
                    json_file.write(json.dumps(data))
                    json_file.close()
                lock.release()
            else:
                print "nothing to update"

            return ''

        except (IOError, KeyError):
            lock.release()
            pass


@app.route('/expiration/<string:uuid>', methods=['GET', 'POST'])
def expiration_date(uuid):
    """
    need to find the correct item to change
    without an index id this would find the first item with the same barcode in the inventory
    which may not be the desired effect
    :param barcode: string representation
    :return:
    """
    lock = LockFile('json/inventory.json')
    if request.method == 'GET':
        try:
            lock.acquire()
            with open('json/inventory.json', 'r') as json_file:
                data = json.load(json_file, encoding='utf-8')  # Get the current inventory.
                json_file.close()

            lock.release()
            index = RestUtils.find_elem(data, 'uuid', uuid)

            if index is not None:
                return data[index]['expirationdate']

        except (IOError, KeyError):
            lock.release()
            return ''
    if request.method == 'POST':
        try:
            expire_date = request.args.get('expires', type=int)
            date = RestUtils.set_expiration(expire_date)
            lock.acquire()
            with open('json/inventory.json', 'r') as json_file:
                data = json.load(json_file, encoding='utf-8')  # Get the current inventory.
                json_file.close()
            lock.release()

            index = RestUtils.find_elem(data, 'uuid', uuid)

            if index is not None:
                data[index]['expirationdate'] = unicode(date)
                lock.acquire()
                with open('json/inventory.json', 'w+') as json_file:
                        json_file.write(json.dumps(data))
                        json_file.close()
                lock.release()
            else:
                print "nothing to update"

        except (IOError, KeyError):
            lock.release()
            pass

    return ''

if __name__ == '__main__':
    app.run(host='localhost', debug=True)
