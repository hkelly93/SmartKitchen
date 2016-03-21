/**
 * Performs all of the REST calls and abstracts it from the controllers.
 * @param  {String} 'restService'  The name of the service.
 * @param  {function} function($http) AngularJS services.
 * @return {Object}                Javascript object to perform REST calls.
 */
app.factory('restService', ['$http',
    function($http) {
        const localUri = 'assets/json/', // URI for local RESTful API.
            openFoodFactsUri = 'http://world.openfoodfacts.org/api/v0/product/', // URI for OFF RESTful api.
            dataType = '.json'; // Datatype to get data back in.

        return {
            /**
             * Gets the kitchen health from json/health.json.
             *
             * TODO: Replace this with a rest call when that gets implemented.
             * @return {null}
             */
            getHealth: function(success, failure) {
                $http({
                    method: 'GET',
                    url: localUri + 'health' + dataType
                }).then(success, failure);
            },
            /**
             * Get the inventory from json/inventory.json. Check for new items and
             * add an alert if there is anything new.
             *
             * TODO: Replace with a real REST call when implemented.
             * @return {null}
             */
            getInventory: function(success, failure) {
                $http({
                    method: 'GET',
                    url: localUri + 'inventory' + dataType
                }).then(success, failure);
            },
            /**
             * Gets the latest inventory from json/inventory.json.
             *
             * TODO: Replace this with a rest call when that gets implemented.
             * @return {null}
             */
            getLatest: function(success, failure) {
                $http({
                    method: 'GET',
                    url: localUri + 'inventory' + dataType
                }).then(success, failure);
            },
            /**
             * Searches for an entry using the Open Food Fact's RESTful API.
             * @param  {String} barcode The barcode that is being looked up
             * @param  {function} success The function to execute on success
             * @param  {function} failure The function to execute on failure
             * @return {null}
             */
            searchBarcode: function(barcode, success, failure) {
                $http({
                    method: 'GET',
                    url: openFoodFactsUri + barcode + dataType
                }).then(success, failure);
            }
        }
    }
]);
