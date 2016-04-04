from os import path, sys
import psutil # check to see if process is running

import json
from flask import Flask, jsonify, make_response
from flask.ext.cors import CORS
import datetime

from util.RestUtils import RestUtils
from messages import Messages

response_data = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'UfrWq8uk7bRvKewY9VwKX7FN'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

app.config['DEBUG'] = True

@app.route('/getFridgeHealth/', methods=['GET'])
def getFridgeHealth():
    if path.isfile('json/health.json'):
        FridgeHealth = 'healthy'
        return FridgeHealth
    else:
        FridgeNotHealth = 'not healthy'
        return FridgeNotHealth
    '''
    fridgeHealth = "healthy"
    return fridgeHealth
    '''

@app.route('/getNetworkHealth/', methods=['GET'])
def getNetworkHealth():
    if path.isfile('json/health.json'):
        NetworkHealth = 'healthy'
        return NetworkHealth
    else:
        NetworkNotHealth = 'not healthy'
        return NetworkNotHealth


@app.route('/setScannerHealth/<string:status>/', methods=['POST'])
def setScannerHealth(status):
    # health = {}
    PROCNAME = 'barcode_scanner'
    running = False
    for proc in psutil.process_iter():
        # check whether the process name matches
        try:
            if proc.name == PROCNAME:
                running = True
        except :
            print 'some sort of error???'
            pass

    try:
        with open('json/health.json', 'r') as json_file:
            health = json.load(json_file, encoding='utf-8')
        with open('json/health.json', 'w') as json_file:
            if running:
                health['scanner'] = status
            else:
                health['scanner'] = 'critical'
            json.dump(health, json_file)
    except (OSError, IOError) as e:
        pass

    return ''


@app.route('/getScannerHealth/')
def getScannerHealth():
    # should check and see if process is running
    # critical if not found
    
    with open('json/health.json', 'r') as json_file:
        health = json.load(json_file, encoding='utf-8')
        return health['scanner']


@app.route('/getInventory/', methods=['GET'])
def getInventory():
    print'get inventory'
    try:
        with open('json/inventory.json', 'r') as json_file:
            inventory = json.loads(json_file.read())  # this will throw correct errors
            return json.dumps(inventory)
    except IOError:
        print 'error'
        return Messages.inventoryNotFound()


# TODO can make all calls like this and save on get/set in url
@app.route('/inventory/<string:barcode>', methods=['DELETE'])
def inventory():
    print'delete inventory'
    # search through database and find item to delete



@app.route('/addInventory/<string:barcode>/', methods=['POST'])
def addInventory(barcode):
    """
    Add an inventory entry for the given barcode.
    """
    inventory = ""
    addedDate = datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S")
    expirationDate = datetime.datetime.today().strftime("%m/%d/%Y")
    print "in add inventory"
    try:
        with open('json/inventory.json', 'r') as json_file:
            inventory = json_file.read()  # Get the current inventory.
            #inventory = json.loads(json_file.read())
            #print inventory
    except IOError:
        print 'cant open file'
        return Messages.inventoryNotFound()

    if inventory != '':  # If the current inventory is not empty
        # Begin adding a new entry.
        #print 'inventory not empty!'
        inventory = inventory.replace("}]", "}, {")

        if not inventory.endswith("\n"):
            inventory += "\n"

        inventory += RestUtils.generateInventoryEntry(
            barcode, addedDate, expirationDate)
    else:  # If the inventory is empty
        inventory = "[{"

        if not inventory.endswith("\n"):
            inventory += "\n"

        inventory += RestUtils.generateInventoryEntry(
            barcode, addedDate, expirationDate)

    try:
        with open('json/inventory.json', 'w') as json_file:
            #print 'trying to write to file'
            json_file.write(inventory)
            #json.dump(data, json_file)
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
    app.run(host='0.0.0.0', port=5000)
