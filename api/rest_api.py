import datetime
import json

from flask import Flask, jsonify, request
from flask.ext.cors import CORS

from util.RestUtils import RestUtils
from messages import Messages

#response_data = {}

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'UfrWq8uk7bRvKewY9VwKX7FN'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)


@app.route('/health/<string:part>/', methods=['GET', 'POST'])
def health(part):
    try:
        with open('json/health.json', 'r') as json_file:
            data = json.load(json_file, encoding='utf-8')

            if request.method == 'POST':
                status = request.args.get('status', type=str)
                data[part] = status

                print status
                with open('json/health.json', 'w') as json_file:
                    json_file.write(json.dumps(data))

                    return 'status set'

            if request.method == 'GET':
                return data[part]

            json_file.close()

    except IOError:
        return Messages.inventoryNotFound()


@app.route('/inventory/', methods=['GET'])
def get_inventory():
    print'get inventory'

    try:
        with open('json/inventory.json', 'r') as json_file:
            data = json.load(json_file)  # this will throw correct errors
            return json.dumps(data)

    except IOError:
        return Messages.inventoryNotFound()


@app.route('/inventory/<string:barcode>/', methods=['DELETE', 'GET', 'POST'])
def inventory(barcode):
    """
    DELETE will remove first item with given barcode from inventory

    GET will return first item with this barcode in inventory

    POST will add to inventory
        will increment quantity of pre existing items
    :param barcode: string representation of barcode
    :param days_till_expire: defaults to None which will set it 30 days from today's date
    :return:

    :usage: http://localhost:5000/inventory/1111?expire=30
    """
    if request.method == 'DELETE':
        try:
            with open('json/inventory.json', 'r') as json_file:
                data = json.load(json_file, encoding='utf-8')  # Get the current inventory.
                json_file.close()

            index = RestUtils.find_elem(data, 'barcode', barcode)

            if index is not None:
                del data[index]
                with open('json/inventory.json', 'w+') as json_file:
                    json_file.write(json.dumps(data))
                    json_file.close()
            else:
                print 'nothing to delete'

            return ''  # TODO should tell you if it actually deleted something?

        except (IOError, KeyError):
            print "file doesnt exist or keyerror"

    if request.method == 'GET':
        try:
            with open('json/inventory.json', 'r') as json_file:
                data = json.load(json_file, encoding='utf-8')
                json_file.close()
                index = RestUtils.find_elem(data, 'barcode', barcode)  # returns index if already exists
                if index is not None:
                    return jsonify(data[index])
                else:
                    return jsonify({})  # TODO what should this return if item doesnt exist?
        except IOError:
            Messages.inventoryNotFound()

    if request.method == 'POST':
        days_till_expire = request.args.get('expire', type=int)

        added_date = datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S")
        expire_date = RestUtils.set_expiration(days_till_expire)

        # TODO add some sort of filelock
        try:
            with open('json/inventory.json', 'r') as json_file:
                data = json.load(json_file, encoding='utf-8')
                json_file.close()

                index = RestUtils.find_elem(data, u"barcode", barcode)  # returns index if already exists

            # there already exists this barcode in the inventory
            if index is not None:
                data[index]['qty'] += 1
                data[index]["expiration"] = unicode(expire_date)
            else:
                # this order matters, layout will add in same order in json
                d = {u'barcode': unicode(barcode),
                     u'added': unicode(added_date),
                     u'expiration': unicode(expire_date),
                     u'qty': 1}

                data.append(d)

            # open up file again to write to it
            with open('json/inventory.json', 'w+') as json_file:
                json_file.write(json.dumps(data, encoding='utf-8'))
                json_file.close()

        except (IOError,KeyError):
            # TODO exception error here
            pass

        return ''  # should this really return the whole dict?


@app.route('/expiration/<string:barcode>/', methods=['PUT'])
def expiration_date(barcode, days_till_expire=None):
    """
    need to find the correct item to change
    without an index id this would find the first item with the same barcode in the inventory
    which may not be the desired effect
    :param barcode: string representation
    :param days: how many days till expiration
    :return:
    """
    days_till_expire = request.args.get('expire', type=int)
    date = RestUtils.set_expiration(days_till_expire)

    try:
        with open('json/inventory.json', 'r') as json_file:
            data = json.load(json_file, encoding='utf-8')  # Get the current inventory.
            json_file.close()

            index = RestUtils.find_elem(data, 'barcode', barcode)

            if index is not None:
                data[index]['expiration'] = unicode(date)
                with open('json/inventory.json', 'w+') as json_file:
                    json_file.write(json.dumps(data))
                    json_file.close()
            else:
                print "nothing to update"

    except IOError:
        pass

    return ''

if __name__ == '__main__':
    app.run(debug=True)
