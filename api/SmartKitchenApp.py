import json
import os.path

from flask import Flask, jsonify

response_data = {}

app = Flask(__name__)


@app.route('/getFridgeHealth/', methods=['GET'])
def getFridgeHealth():
    if os.path.isfile('SmartKitchen-master/ui/app/assets/json/health.json'):
        FridgeHealth ='healthy'
        return FridgeHealth
    else:
        FridgeNotHealth = 'not healthy'
        return FridgeNotHealth

    fridgeHealth = "healthy"
    return fridgeHealth

@app.route('/getNetworkHealth/')
def getNetworkHealth():
    if os.path.isfile('SmartKitchen-master/ui/app/assets/json/health.json'):
        NetworkHealth ='healthy'
        return NetworkHealth
    else:
        NetworkNotHealth = 'not healthy'
        return NetworkNotHealth




@app.route('/getScannerHealth/')
def getScannerHealth():
    if os.path.isfile('SmartKitchen-masterg/scanner.json'):
        ScannerkHealth ='healthy'
        return ScannerHealth
    else:
        ScannerNotHealth = 'not healthy'
        return ScannerNotHealth


@app.route('/getInventory/')
def getInventory():
    with open('json/inventory.json') as json_file:
        inventory = json.load(json_file)
        return json.dumps(inventory)


@app.route('/addInventory/<string:barcode>/')
def addInventory(barcode):
    inventory={}
    with open('SmartKitchen-master/ui/app/assets/json/inventory.json', 'r') as json_file:
        inventory = json.load(json_file, encoding='utf-8')
    with open('SmartKitchen-master/ui/app/assets/json/inventory.json', 'w') as json_file:
        inventory.append({"barcode": "8965342"})
        json.dump(inventory, json_file)


@app.route('/setExpirationDate/<string:date>/')
def setExpirationDate(date):
    return "";


if __name__ == '__main__':
    app.run(debug=True)
