#Smart Kitchen

## Project Goals

Creation of an easier way to inventory and keep track of what products you have in your kitchen. Keeping it simple by only requiring adding when a new product is purchased and deleting the item when it is used up or thrown away.

## Project Features
* Web Interface
* Alert system for new events
* Camera based scanner
* Cheap, easy to get hardware (~$60)
* Wireless capability
* Low power usage
* Leverages large product database
* Ability to add, edit, and delete items
* Visual acknowledgement of barcode scan
* Visual status of system through LEDs
* Power saving feature which is disabled by motion or control from the Web Interface

## Project Design
![Project Design](http://i.imgur.com/D9fnnHq.png)

## File Structure

### api/json/health.json
Written by Harrison Kelly, this file contains the health for all of the components (Fridge, Network, and Scanner). This file is used to be easily accessible by the UI since JSON gets converted to JavaScript objects easily.

### api/json/inventory.json
Written by Harrison Kelly, this file contains the inventory of the Kitchen. This file is used to be easily accessible by the UI since JSON gets converted to JavaScript objects easily. The keys in this file are: name, barcode, uuid, added, and expiration date.

### api/util/RestUtils.py
Written by Brian Day and Harrison Kelly, this file contains utility functions used by rest_api

### api/util/messages.py
Written by Harrison Kelly, this file was created to make internationalizing the REST API easier.

### api/util/rest_api.py
Written by Brian Day, this file contains REST api to allow communication between webpage and scanner

### scanner/Hardware.py
Written by Brian Day, this file was created to control the hardware aspects of the Raspberry pi.

### scanner/Scanner.py
Written by Brian Day, this file contains all needed code to control the raspberry pi and camera that is used to read barcodes. Main file of the hardware side of the project. Implements all the features except those dealing directly with database of items. This program is multi threaded to allow all aspects to be run at the same time and not interfere with each other.
* The main code is checking all the states of the threads and also looking for a request from the server in which to restart the program if it is in eco-mode. Status_thread  controls displaying of current status on LED on the raspberrypi.
* Timer_thread allows for a timer to allow program to reach eco-mode when has not been interacted with in sometime.
* Scanner_thread creates a subprocess that runs the zbarcam program which will block until a valid barcode is read.
* Sensor_thread( motion sensor) allows raspberry pi to be constantly looking for motion detected fro PIR sensor.

### ui/app/assets/css/stylesheet.css
Written by Harrison Kelly, this file contains the CSS stylesheet for the UI.

### ui/app/assets/js/smartKitchen.js
Written by Harrison Kelly, this file creates the AngularJs application, the Severity constant (Used for determining whether an Alert is “Info”, “Warning”, or “Critical”.), and the Status constant (Used for determining if a health item is “Healthy”, “Warning”, “Critical”, or “Weak”.)

### ui/app/controllers/healthController.js
Written by Harrison Kelly, this file controls the Kitchen health part of the project and is required for updating and showing the health. When this controller is first loaded, it gets the fridge, scanner, and network health via the REST api. It then loads itself into the refreshData Service (see below) to allow the same process to occur every five seconds. This controller is also responsible for showing and hiding the reset button, which resets the Scanner when it is in eco mode.

### ui/app/controllers/inventoryController.js
Written by Harrison Kelly, this file controls the inventory part of the project and is required for updating and showing the inventory. When this controller is first loaded, it attempts to get the inventory from the cache (to prevent unnecessary REST calls to openfoodfacts) and then begins generating the inventory. This controller also loads itself into the refreshData Service (see below) to allow the same process to occur every five seconds.

### ui/app/controllers/mainController.js
Written by Harrison Kelly, this file is the main controller for the project and contains the Alert code and other global code. This controller is responsible for showing the loading indicators on the panels during REST calls and generating the popup for editing an inventory item.

### ui/app/controllers/navController.js
Written by Harrison Kelly, this file is the navigation controller for the project and is responsible for updating the inventory count in the navigation bar.

### ui/app/objects/Item.js
Written by Harrison Kelly, this file is used as an object for an Item. It contains all the properties (name, expiration date, uuid, etc.) for the item.

### ui/app/objects/Alert.js
Written by Harrison Kelly, this file is used as an object for an Alert. It contains all of the properties (message, severity, time) for the Alert.

### ui/app/services/cacheService.js
Written by Harrison Kelly, this file is used for caching the inventory so that when the page is refreshed or reloaded, there are no necessary REST calls to openfoodfacts.org unless if there is an addition to the inventory.

### ui/app/services/logService.js
Written by Harrison Kelly, this file is used for logging to the JavaScript console to make debugging and logging simpler. The service was created to act similar to the Python and Java logging frameworks and allows for a global log level to be set. It also has different methods for logging (debug, info, warn, critical) and only shows messages equal to or greater than the global log level.

### ui/app/services/messagesService.js
Written by Harrison Kelly, this file is used for localization and currently supports: English, Spanish, and French (uses the browser’s locale to determine what to show).

### ui/app/services/refreshDataService.js
Written by Harrison Kelly, this file is used for registering each controller and calling the load method to refresh the data every five seconds.

### ui/app/services/restService.js
Written by Harrison Kelly, this file contains all of the REST calls and returns promises back to the controller.

### ui/app/index.php
Written by Harrison Kelly, this file is the main HTML for the application.

### ui/app/webserver.py
Written by Brian Day, easy way to test web server.

