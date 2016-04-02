import json
import os.path

from flask import Flask, jsonify, make_response
import datetime

from util.RestUtils import RestUtils
from messages import Messages

response_data = {}

app = Flask(__name__)


@app.route('/getFridgeHealth/', methods=['GET'])
def getFridgeHealth():
    if os.path.isfile('json/health.json'):
        FridgeHealth = 'healthy'
        return FridgeHealth
    else:
        FridgeNotHealth = 'not healthy'
        return FridgeNotHealth

    fridgeHealth = "healthy"
    return fridgeHealth


@app.route('/getNetworkHealth/', methods=['GET'])
def getNetworkHealth():
    if os.path.isfile('json/health.json'):
        NetworkHealth = 'healthy'
        return NetworkHealth
    else:
        NetworkNotHealth = 'not healthy'
        return NetworkNotHealth


@app.route('/setScannerHealth/<string:status>/', methods=['POST'])
def setScannerHealth(status):
    health = {}

    with open('json/health.json', 'r') as json_file:
        health = json.load(json_file, encoding='utf-8')
    with open('json/health.json', 'w') as json_file:
        health['scanner'] = status
        json.dump(health, json_file)

    return ''


@app.route('/getScannerHealth/')
def getScannerHealth():
    with open('json/health.json', 'r') as json_file:
        health = json.load(json_file, encoding='utf-8')
        return health['scanner']

    '''
    # TODO should this really be a file????!!! or should the scanner POST to this?
    if os.path.isfile('SmartKitchen/scanner.json'):
        ScannerkHealth ='healthy'
        return ScannerHealth
    else:
        ScannerNotHealth = 'not healthy'
        return ScannerNotHealth
    '''


@app.route('/getInventory/')
def getInventory():
    print 'get inventory'
    with open('json/inventory.json') as json_file:
        inventory = json.load(json_file)
        return json.dumps(inventory)


# added methods=['POST'] to not get a 405 error
@app.route('/addInventory/<string:barcode>/', methods=['POST'])
def addInventory(barcode):
    """
    Add an inventory entry for the given barcode.
    """
    inventory = ""
    addedDate = datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S")

    try:
        with open('json/inventory.json', 'r') as json_file:
            inventory = json_file.read()  # Get the current inventory.
    except IOError:
        return Messages.inventoryNotFound()

    if (inventory != ""):  # If the current inventory is not empty
        # Begin adding a new entry.
        inventory = inventory.replace("}]", "}, {")

        if not inventory.endswith("\n"):
            inventory += "\n"

        inventory += RestUtils.generateInventoryEntry(barcode, addedDate)
    else:  # If the inventory is empty
        inventory = "[{"

        if not inventory.endswith("\n"):
            inventory += "\n"

        inventory += RestUtils.generateInventoryEntry(barcode, addedDate)

    try:
        with open('json/inventory.json', 'w') as json_file:
            json_file.write(inventory)
    except IOError:
        return Messages.inventoryNotFound()

    return inventory


@app.route('/setExpirationDate/<string:date>/')
def setExpirationDate(date):
    return ''

'''
@app.errorhandler(405)
def not_found(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)
'''
if __name__ == '__main__':
    app.run(debug=True)
