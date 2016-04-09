from os import path, sys
import psutil # check to see if process is running
from filelock import FileLock
import json
from flask import Flask, jsonify, make_response
from flask.ext.cors import CORS
import datetime
from flask import request
from util.RestUtils import RestUtils
from messages import Messages

import logging

response_data = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'UfrWq8uk7bRvKewY9VwKX7FN'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

app.config['DEBUG'] = True

# logging
file_handler = logging.FileHandler('app.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)


@app.route('/fridgeHealth/', methods=['GET', 'POST'])
def fridgeHealth():
    if request.method == 'GET':
        fridgeHealth = 'healthy'
        return fridgeHealth
    if request.method == 'POST':
        fridgeHealth = request.data
        return fridgeHealth


@app.route('/networkHealth/', methods=['GET', 'POST'])
def networkHealth():
    if request.method == 'GET':
        networkHealth = 'healthy'
        return networkHealth
    if request.method == 'POST':
        networkHealth = request.data
        return networkHealth


@app.route('/scannerHealth/<string:status>/', methods=['GET', 'POST'])
def scannerHealth(status):
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

'''
# TODO can make all calls like this and save on get/set in url
@app.route('/inventory/<string:barcode>', methods=['DELETE'])
def inventory():
    print'delete inventory'
    # search through database and find item to delete

'''

@app.route('/addInventory/<string:barcode>/', methods=['POST'])
def addInventory(barcode):
    """
    Add an inventory entry for the given barcode.
    """
    inventory = ""
    addedDate = datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S")
    expirationDate = datetime.datetime.today().strftime("%m/%d/%Y")
    #print "in add inventory"
    try:
        with FileLock('json/inventory.json'):
            try:
                with open('json/inventory.json', 'r') as json_file:
                    inventory = json_file.read()  # Get the current inventory.
                    #inventory = json.loads(json_file.read())
                    #print inventory
            except IOError:
                #print 'cant open file'
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

    except Exception as e:
        return e

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
