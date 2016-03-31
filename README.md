# SmartKitchen

Monday March 28, 2015
=====================

Harrison Kelly -- Fixed a UI caching issue and stubbed out the async calls for the new REST api. Also
    made a slight modification to the REST api and connected the /getLatestInventory/ call.

Tuesday March 29, 2015
======================

Harrison Kelly -- Got rid of the unused icons and changed the ordering of the Latest Inventory so that
    it was actually the latest and not the first three items, also changed the ordering of the Inventory
    to show the latest at the top.

Wed March 30th, 2016

Brian Day -- started from scratch on scanner part of project it is now correctly threaded. Useing zbarimg directly now
    and piping its output into our code. Scanner is also connected to the rest api, scanner health POST's to the
    rest api for now, may change

