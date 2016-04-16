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

        $scope.latest = [];
        $scope.inventory = [];
        $scope.cache = cache.getCache("inventoryController-inventory");

        function createItem(response) {
            $rootScope.toggleBusy(false);
            var barcode = response.data.code,
                product = response.data.product.product_name,
                item = {
                    name: response.data.product.product_name,
                    image: response.data.product.image_front_thumb_url,
                    expires: response.data.args.expirationdate,
                    expiresDateVal: toDate(response.data.args.expirationdate),
                    barcode: barcode,
                    uuid: response.data.args.uuid
                };

            $scope.cache[barcode] = item;
            $scope.inventory.push(item);

            if ($scope.latest.length < 4) {
                $scope.latest.push(item);
            }

            $rootScope.addAlert(0, product + " was added to the inventory.");
            $rootScope.toggleInventoryBusy(false);
        }

        function inventoryError(response) {
            $rootScope.addAlert(SEVERITY.WARNING, "Something went wrong and the inventory could not be found.");
            $rootScope.toggleBusy(false);
            $rootScope.toggleInventoryBusy(false);
        }

        /**
         * Load the data from the controller into the view.
         * @return {null}
         */
        $scope.load = function(firstLoad) {
            $rootScope.toggleInventoryBusy(true);

            var showBusy = false;
            if (firstLoad) { // init
                $rootScope.toggleBusy(true);
                showBusy = true;
            }

            var promise = restService.getInventory();

            promise.success(function(response) {
                $scope.inventory = [];
                $scope.latest = [];
                $scope.expirationDates = {};

                var index = response.data.length - 1,
                    maxForLatest = (response.data.length < 3) ? response.data.length : response.data.length - 4,
                    itemExists = false,
                    barcode,
                    uuid,
                    expirationDate;

                for (index; index > 0; index--) {
                    barcode = response.data[index].barcode;
                    uuid = response.data[index].uuid;
                    expirationDate = response.data[index].expirationdate;

                    // Search in the cache first.
                    if (barcode in $scope.cache) {
                        var entity = $scope.cache[barcode];

                        // Set the expiration date just in case it is different
                        entity.expires = expirationDate;
                        entity.expiresDateVal = toDate(expirationDate);
                        entity.uuid = uuid;

                        $scope.inventory.push(entity);

                        if (index > maxForLatest) {
                            $scope.latest.push(entity);
                        }

                        logService.debug('inventoryController', 'Found ' + barcode + ' in cache.');

                    } else {
                        logService.debug('inventoryController', 'REST call for barcode ' + barcode);

                        // Search for the barcode.

                        if (showBusy) {
                            $rootScope.toggleBusy(true);
                        }

                        $rootScope.toggleInventoryBusy(true);
                        var promise = restService.searchBarcode(barcode, uuid, expirationDate);
                        promise.success(createItem);
                        promise.error(inventoryError);
                    }
                }

                if (showBusy) {
                    $rootScope.toggleBusy(false);
                }

                $rootScope.toggleInventoryBusy(false);
            });

            promise.error(function(response) {
                $rootScope.addAlert(SEVERITY.CRITICAL, "Something went wrong and the inventory could not be found.");

                if (showBusy) {
                    $rootScope.toggleBusy(false);
                }
                $rootScope.toggleInventoryBusy(false);
            });

            if (firstLoad) {
                $rootScope.toggleBusy(false);
            }

            $rootScope.toggleInventoryBusy(false);
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

            var promise = restService.removeFromInventory(item);

            promise.success(function() {
                $scope.load(true);
                $rootScope.toggleBusy(false);
            });

            promise.error(function() {
                $rootScope.toggleBusy(false);
                $rootScope.addAlert(SEVERITY.CRITICAL, 'Could not delete ' + item.name + '.');
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

        $scope.load(true);

        // Add this controller to the loaded controllers.
        refreshData.loadController('inventoryController');
        refreshData.refreshData('inventoryController', 'Refreshing inventory data.');

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