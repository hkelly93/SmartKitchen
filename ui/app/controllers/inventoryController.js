/* jshint esversion: 6 */

/**
 * Controls the inventory and refreshes the data.
 * @param  {String} 'healthController' Controller name
 * @param  {function} AngularJS services
 * @return {null}
 */
app.controller('inventoryController', ['$scope', '$rootScope', 'refreshData', 'cache', 'restService', 'logService', 'SEVERITY',
    function($scope, $rootScope, refreshData, cache, restService, logService, SEVERITY) {
        'use strict';

        // Add this controller to the loaded controllers.
        refreshData.loadController('inventoryController');
        refreshData.refreshData('inventoryController', 'Refreshing inventory data.');

        $scope.latest = [];
        $scope.inventory = [];
        $scope.cache = cache.getCache("inventoryController-inventory");

        /**
         * Load the data from the controller into the view.
         * @return {null}
         */
        $scope.load = function() {
            var expirationDates = {};

            function createItem(response) {
                var product = response.data.product,
                    barcode = response.data.code,
                    item = {
                        name: product.product_name,
                        image: product.image_front_thumb_url,
                        expires: expirationDates[barcode],
                        expiresDateVal: toDate(expirationDates[barcode]),
                        barcode: barcode
                    };

                $scope.newList.push(item);
                $scope.cache[barcode] = item;
            }

            function latestInventoryError(response) {
                $rootScope.addAlert(SEVERITY.WARNING, "Something went wrong and the latest inventory could not be found.");
            }

            var promise = restService.getLatest();

            promise.success(function(response) {
                $scope.newList = [];

                // Get all of the expiration dates.
                for (var index = 0; index < response.data.length; index++) {
                    var barcode = response.data[index].barcode;
                    var expiration = response.data[index].expirationdate;

                    expirationDates[barcode] = expiration;
                }

                // Get the last three items.
                var maxLength = (response.data.length < 3) ? response.data.length : response.data.length - 4,
                    i = response.data.length - 1,
                    elBarcode,
                    expiresDate,
                    item;

                for (i; i > maxLength; i--) {
                    elBarcode = response.data[i].barcode;

                    // Search in the cache first.
                    if (elBarcode in $scope.cache) {
                        item = $scope.cache[elBarcode];

                        // Set the expiration date just in case it is different
                        item.expirationdate = response.data[i].expirationdate;
                        item.expiresDateVal = toDate(response.data[i].expirationdate);

                        $scope.newList.push(item);
                    } else {
                        logService.debug('inventoryController', 'REST call for barcode ' + elBarcode);

                        var promise = restService.searchBarcode(elBarcode);
                        promise.success(createItem);
                        promise.error(latestInventoryError);
                    }
                }

                $scope.$watch('newList', function(n) {
                    if (n.length === 3) {
                        $scope.latest = $scope.newList;
                    }
                }, true);
            });

            promise.error(function(response) {
                $rootScope.addAlert(SEVERITY.WARNING, "Something went wrong and the latest inventory could not be found.");
            });

            promise = restService.getInventory();

            promise.success(function(response) {
                $scope.inventory = [];

                function createProduct(response) {
                    var barcode = response.data.code,
                        product = response.data.product.product_name,
                        item = {
                            name: response.data.product.product_name,
                            image: response.data.product.image_front_thumb_url,
                            expires: expirationDates[barcode],
                            expiresDateVal: toDate(expirationDates[barcode]),
                            barcode: barcode
                        };

                    $scope.cache[barcode] = item;
                    $scope.inventory.push(item);

                    $rootScope.addAlert(0, product + " was added to the inventory.");
                }

                function inventoryError(response) {
                    $rootScope.addAlert(SEVERITY.WARNING, "Something went wrong and the inventory could not be found.");
                }

                var item,
                    index,
                    barcode,
                    product;

                for (item = response.data.length - 1; item > 0; item--) {
                    index = $scope.inventory.indexOf(response.data[item]);

                    if (index < 0) {
                        barcode = response.data[item].barcode;

                        // Search in the cache first.
                        if (barcode in $scope.cache) {
                            var entity = $scope.cache[barcode];

                            // Set the expiration date just in case it is different
                            entity.expirationdate = response.data[item].expirationdate;
                            entity.expiresDateVal = toDate(response.data[item].expirationdate);

                            $scope.inventory.push(entity);
                            logService.debug('inventoryController', 'Found ' + barcode + ' in cache.');
                        } else {
                            logService.debug('inventoryController', 'REST call for barcode ' + barcode);
                            var promise = restService.searchBarcode(barcode);
                            promise.success(createProduct);
                            promise.error(inventoryError);
                        }
                    }
                }
            });

            promise.error(function(response) {
                $rootScope.addAlert(SEVERITY.CRITICAL, "Something went wrong and the inventory could not be found.");
            });
        };

        /**
         * Returns whether or not the inventory has changed.
         * @return {boolean} Whether or not the inventory has changed.
         */
        $scope.isInventoryEqual = function() {
            var equal = false;

            if ($scope.newList.length == $scope.latest.length) {
                for (var item in $scope.newList) {
                    var element = $scope.newList[item].barcode;

                    var found = false;
                    for (var otherItem in $scope.latest) {
                        var otherElement = $scope.latest[otherItem].barcode;

                        if (otherElement == element) {
                            found = true;
                            break;
                        }
                    }
                    equal = found;
                }
            }

            return equal;
        };

        $scope.deleteItem = function(item) {
            logService.debug('inventoryController', 'Deleting barcode ' + item.barcode);
            var promise = restService.removeFromInventory(item.barcode);

            promise.success(function() {
                // TODO
            });

            promise.error(function() {
                // TODO
            });
        };

        /**
         * Converts date from mm/dd/yyyy format to a different string format.
         * @param  {String} date   The date to convert
         * @return {String}        The String representation of "date".
         */
        var toDate = function(date) {
            var dateParts = date.split("/");

            if (dateParts.length != 3) {
                logService.warning('inventoryController', 'Invalid date, ' + date + ' found.');
                return '';
            }

            if (date.length != 10) {
                logService.warning('inventoryController', 'Invalid date, ' + date + ' found.');
                return '';
            }

            // The subtraction by one for the month is due to the fact that JavaScript starts months at zero.
            var dateObj = new Date(dateParts[2], dateParts[0] - 1, dateParts[1]),
                year = dateObj.getFullYear().toString(),
                month = (dateObj.getMonth() + 1).toString(),
                day = dateObj.getDate().toString();

            if (month.length === 1) {
                month = '0' + month;
            }

            if (day.length === 1) {
                day = '0' + day;
            }
            return dateObj;
        };

        $scope.load();

        // Register event handlers
        $rootScope.$on("refreshInventory", function() {
            $scope.load();
        });

        var saveCache = function() {
            cache.setCache("inventoryController-inventory", $scope.cache);
        };

        window.onbeforeunload = saveCache;

        // Cleanup
        $scope.$on("$destroy", function() {
            saveCache();
            refreshDataService.unloadController('inventoryController');
        });
}]);