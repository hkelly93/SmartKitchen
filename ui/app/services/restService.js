/* jshint esversion: 6 */
/* global Item, token */
/**
 * Performs all of the REST calls and abstracts it from the controllers.
 * @param  {String} 'restService'  The name of the service.
 * @param  {function} function($http) AngularJS services.
 * @return {Object}                Javascript object to perform REST calls.
 */
app.factory('restService', ['$http', '$q',
    function ($http, $q) {
        'use strict';

        var localRestUri = 'http://192.168.2.38:5000/',
            openFoodFactsUri = 'http://world.openfoodfacts.org/api/v0/product/', // URI for OFF RESTful api.
            dataType = '.json', // Datatype to get data back in.
            timeout = 30 * 1000; // Timeout in milliseconds.

        var deferrer = {
            // http://ericnish.io/blog/add-success-and-error-to-angular-promises/
            decorate: function (promise) {
                promise.success = function (callback) {
                    promise.then(callback);

                    return promise;
                };

                promise.error = function (callback) {
                    promise.then(null, callback);

                    return promise;
                };
            },
            defer: function () {
                var deferred = $q.defer();

                this.decorate(deferred.promise);

                return deferred;
            }
        };

        return {
            /**
             * Wrapper for a promise.
             * @param  {XMLHttpRequest} request Request to promise.
             * @param  {Object} args additional arguments to pass in the response.
             * @return       Promise of HTTP request.
             */
            defer: function (request, args) {
                var dfd = deferrer.defer();

                request.then(function (res) {
                    try {
                        res.data.args = args;
                    } catch (err) {

                    }
                    return dfd.resolve(res);
                }, function (err) {
                    return dfd.reject(err);
                });

                return dfd.promise;
            },
            /**
             * Gets the full inventory from json/inventory.json.
             *
             * @return {deferrer} The http GET request promise.
             */
            getInventory: function () {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'inventory/' + '?token=' + token,
                    timeout: timeout
                }), {});
            },
            /**
             * Searches for an entry using the Open Food Fact's RESTful API.
             * @param  {String} barcode The barcode that is being looked up
             * @param  {String} uuid The uuid for the item being searched.
             * @param  {String} expirationDate The expiration date of the item being searched.
             * @param  {String} name The name of the item being searched.
             * @return {deferrer} The http GET request promise.
             */
            searchBarcode: function (barcode, uuid, expirationDate, name) {
                return this.defer($http({
                    method: 'GET',
                    url: openFoodFactsUri + barcode + dataType,
                    timeout: timeout
                }), {
                    'uuid': uuid,
                    'expirateiondate': expirationDate,
                    'name': name
                }, {});
            },
            /**
             * Returns the fridge health.
             * @return {deferrer} The http GET request promise.
             */
            getFridgeHealth: function () {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'health/fridge' + '?token=' + token,
                    timeout: timeout
                }), {});
            },
            /**
             * Returns the network health.
             * @return {deferrer} The http GET request promise.
             */
            getNetworkHealth: function () {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'health/network' + '?token=' + token,
                    timeout: timeout
                }), {});
            },
            /**
             * Returns the scanner health.
             * @return {deferrer} The http GET request promise.
             */
            getScannerHealth: function () {
                return this.defer($http({
                    method: 'GET',
                    url: localRestUri + 'health/scanner' + '?token=' + token,
                    timeout: timeout
                }));
            },
            /**
             * Remove an item from the inventory.
             * @param  {Object} item      The item to delete.
             * @return {deferrer}      The http DELETE request promise.
             */
            removeFromInventory: function (item) {
                return this.defer($http({
                    method: 'DELETE',
                    url: localRestUri + 'inventory/' + item.uuid + '?token=' + token,
                    timeout: timeout
                }), {});
            },
            /**
             * Set the expiration date of an item.
             * @param  {Item} item      The object to set the expiration date on.
             * @return {deferrer}      The http POST request promise.
             */
            updateItem: function (item) {
                var start = moment(new Date()),
                    end = moment(item.getExpiresDate()),
                    diff = end.diff(start, 'days');

                if (diff > 0) {
                    diff += 1;
                }

                return this.defer($http({
                    method: 'PUT',
                    url: localRestUri + 'inventory/' + item.uuid + '?expires=' + diff + '&name=' + item.getName() + '&token=' + token,
                    data: 'barcode=' + item.uuid + '&expires=' + diff + '&name=' + item.getName() +  + '&token=' + token,
                    timeout: timeout
                }), {});
            },
            /**
             * Restart the scanner.
             * @returns {deferrer} The http POST request promise.
             */
            restartScanner: function () {
                return this.defer($http({
                    method: 'POST',
                    url: localRestUri + 'restart/' + '?token=' + token,
                    timeout: timeout
                }), {});
            }
        };
    }]);