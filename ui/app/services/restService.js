/* jshint esversion: 6 */
/**
 * Performs all of the REST calls and abstracts it from the controllers.
 * @param  {String} 'restService'  The name of the service.
 * @param  {function} function($http) AngularJS services.
 * @return {Object}                Javascript object to perform REST calls.
 */
app.factory('restService', ['$http', '$q',
    function($http, $q) {
        'use strict';

        var localUri = 'assets/json/', // URI for local RESTful API.
            localRestUri = 'http://localhost:5000/', //http://raspberrypi.local:5000/',
            openFoodFactsUri = 'http://world.openfoodfacts.org/api/v0/product/', // URI for OFF RESTful api.
            dataType = '.json', // Datatype to get data back in.
            timeout = 30 * 1000; // Timeout in milliseconds.

        var deferrer = {
            // http://ericnish.io/blog/add-success-and-error-to-angular-promises/
            decorate: function(promise) {
                promise.success = function(callback) {
                    promise.then(callback);

                    return promise;
                };

                promise.error = function(callback) {
                    promise.then(null, callback);

                    return promise;
                };
            },
            defer: function() {
                var deferred = $q.defer();

                this.decorate(deferred.promise);

                return deferred;
            }
        };

        return {
            /**
             * Wrapper for a promise.
             * @param  {http} request Request to promise.
             * @return {HttpPromise}      Promise of HTTP request.
             */
            defer: function(request, args) {
                var dfd = deferrer.defer();

                request.then(function(res) {
                    try {
                        res.data.args = args;
                    } catch (err) {

                    }
                    return dfd.resolve(res);
                }, function(err) {
                    return dfd.reject(err);
                });

                return dfd.promise;
            },
            /**
             * Gets the latest inventory from json/inventory.json.
             *
             * @return {HttpPromise} The http GET request promise.
             */
            getLatest: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'inventory/',
                    timeout: this.timeout
                }));
            },
            /**
             * Gets the full inventory from json/inventory.json.
             *
             * @return {HttpPromise} The http GET request promise.
             */
            getInventory: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'inventory/',
                    timeout: this.timeout
                }));
            },
            /**
             * Searches for an entry using the Open Food Fact's RESTful API.
             * @param  {String} barcode The barcode that is being looked up
             * @param  {function} success The function to execute on success
             * @param  {function} failure The function to execute on failure
             * @return {HttpPromise} The http GET request promise.
             */
            searchBarcode: function(barcode, uuid, expirationDate) {
                return this.defer($http({
                    method: 'GET',
                    url: openFoodFactsUri + barcode + dataType,
                    timeout: this.timeout
                }), {
                    'uuid': uuid,
                    'expirateiondate': expirationDate
                });
            },
            /**
             * Returns the fridge health.
             * @return {HttpPromise} The http GET request promise.
             */
            getFridgeHealth: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'health/fridge',
                    timeout: this.timeout
                }));
            },
            /**
             * Returns the network health.
             * @return {HttpPromise} The http GET request promise.
             */
            getNetworkHealth: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'health/network',
                    timeout: this.timeout
                }));
            },
            /**
             * Returns the scanner health.
             * @return {HttpPromise} The http GET request promise.
             */
            getScannerHealth: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'health/scanner',
                    timeout: this.timeout
                }));
            },
            /**
             * Remove an item from the inventory.
             * @param  {Object} item      The item to delete.
             * @return {HttpPromise}      The http DELETE request promise.
             */
            removeFromInventory: function(item) {
                return this.defer($http({
                    method: 'DELETE',
                    url: localRestUri + 'inventory/' + item.barcode,
                    timeout: this.timeout
                }));
            },
            /**
             * Set the expiration date of an item.
             * @param  {Object} item      The object to set the expiration date on.
             * @return {HttpPromise}      The http POST request promise.
             */
            setExpirationDate: function(item) {
                var start = moment(new Date()),
                    end = moment(item.expiresDateVal),
                    diff = end.diff(start, 'days') + 1;

                console.log(diff);
                return this.defer($http({
                    method: 'POST',
                    url: localRestUri + 'expiration/' + item.barcode + '?expires=' + diff,
                    data: 'barcode=' + this.barcode + '&expires=' + diff,
                    timeout: this.timeout
                }));
            },
        };
}]);