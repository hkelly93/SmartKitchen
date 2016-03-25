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
            openFoodFactsUri = 'http://world.openfoodfacts.org/api/v0/product/', // URI for OFF RESTful api.
            dataType = '.json'; // Datatype to get data back in.

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
             * @return {promise}      Promise of HTTP request.
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
             * @return {promise} The http GET request promise.
             */
            getHealth: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localUri + 'health' + dataType
                }));
            },
            /**
             * Get the inventory from json/inventory.json. Check for new items and
             * add an alert if there is anything new.
             *
             * TODO: Replace with a real REST call when implemented.
             * @return {promise} The http GET request promise.
             */
            getInventory: function() {
                return this.defer($http({
                    method: 'GET',
                    url: localUri + 'inventory' + dataType
                }));
            },
            /**
             * Gets the latest inventory from json/inventory.json.
             *
             * TODO: Replace this with a rest call when that gets implemented.
             * @return {promise} The http GET request promise.
             */
            getLatest: function(success, failure) {
                return this.defer($http({
                    method: 'GET',
                    url: localUri + 'inventory' + dataType
                }));
            },
            /**
             * Searches for an entry using the Open Food Fact's RESTful API.
             * @param  {String} barcode The barcode that is being looked up
             * @param  {function} success The function to execute on success
             * @param  {function} failure The function to execute on failure
             * @return {promise} The http GET request promise.
             */
            searchBarcode: function(barcode) {
                return this.defer($http({
                    method: 'GET',
                    url: openFoodFactsUri + barcode + dataType
                }));
            }
        };
    }
]);
