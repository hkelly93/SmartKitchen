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

        const localUri = 'assets/json/', // URI for local RESTful API.
            localRestUri = 'http://localhost:5000/',
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
            defer: function(request) {
                var dfd = deferrer.defer();

                request.then(function(res) {
                    return dfd.resolve(res);
                }, function(err) {
                    return dfd.reject(err);
                });

                return dfd.promise;
            },
            /**
             * Gets the kitchen health from json/health.json.
             *
             * TODO: Replace this with a rest call when that gets implemented.
             * @return {HttpPromise} The http GET request promise.
             */
            getHealth: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localUri + 'health' + dataType,
                    timeout: this.timeout
                }));
            },
            /**
             * Get the inventory from json/inventory.json. Check for new items and
             * add an alert if there is anything new.
             *
             * TODO: Replace with a real REST call when implemented.
             * @return {HttpPromise} The http GET request promise.
             */
            // getInventory: function() {
            //     return this.defer($http({
            //         method: 'GET',
            //         url: localUri + 'inventory' + dataType,
            //         timeout: this.timeout
            //     }));
            // },
            /**
             * Gets the latest inventory from json/inventory.json.
             *
             * TODO: Replace this with a rest call when that gets implemented.
             * @return {HttpPromise} The http GET request promise.
             */
            getLatest: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'getInventory/',
                    timeout: this.timeout
                }));
            },
            getInventory: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'getInventory/',
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
            searchBarcode: function(barcode) {
                return this.defer($http({
                    method: 'GET',
                    url: openFoodFactsUri + barcode + dataType,
                    timeout: this.timeout
                }));
            },

            // Soon to be implemented.
            getFridgeHealth: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'getFridgeHealth/',
                    timeout: this.timeout
                }));
            },
            getNetworkHealth: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'getNetworkHealth/',
                    timeout: this.timeout
                }));
            },
            getScannerHealth: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'getScannerHealth/',
                    timeout: this.timeout
                }));
            },
            removeFromInventory: function(item) {
                return this.defer($http({
                    method: 'DELETE',
                    url: localRestUri + 'deleteFromInventory/' + item.barcode + '/',
                    timeout: this.timeout
                }));
            },
            setExpirationDate: function(item) {
                var itemData = $.param({
                    json: JSON.stringify({
                        barcode: item.barcode,
                        expirationdate: item.expirationdate
                    })
                });
                return this.defer($http({
                    method: 'PUT',
                    url: localRestUri + 'setExpirationDate/' + item.barcode + '/' + item.expirationdate + '/',
                    date: itemDate,
                    timeout: this.timeout
                }));
            },
        };
    }
]);
