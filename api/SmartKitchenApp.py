import json
import os.path

from flask import Flask, jsonify,make_response

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
    if os.path.isfile('SmartKitchen/ui/app/assets/json/health.json'):
        NetworkHealth ='healthy'
        return NetworkHealth
    else:
        NetworkNotHealth = 'not healthy'
        return NetworkNotHealth




@app.route('/getScannerHealth/')
def getScannerHealth():
    if os.path.isfile('SmartKitchen/scanner.json'):
        ScannerkHealth ='healthy'
        return ScannerHealth
    else:
        ScannerNotHealth = 'not healthy'
        return ScannerNotHealth


@app.route('/getInventory/')
def getInventory():
    print 'get inventory'
    with open('json/inventory.json') as json_file:
        inventory = json.load(json_file)
        return json.dumps(inventory)


@app.route('/addInventory/<string:barcode>/', methods=['POST'])  # added the method at the end to not get a 405 error
def addInventory(barcode):
    inventory={}
    with open('json/inventory.json', 'r') as json_file:
        inventory = json.load(json_file, encoding='utf-8')
    with open('json/inventory.json', 'w') as json_file:
        inventory.append({"barcode": barcode})
        json.dump(inventory, json_file)

@app.route('/setExpirationDate/<string:date>/')
def setExpirationDate(date):
    return "";
'''
@app.errorhandler(405)
def not_found(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)
'''
if __name__ == '__main__':
    app.run(debug=True)
