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
            restService.getLatest(function success(response) {
                $scope.newList = [];
                var maxLength = (response.data.length < 3) ? response.data.length : 3,
                    i = 0,
                    elBarcode,
                    expiresDate,
                    item;

                for (i; i < maxLength; i++) {
                    elBarcode = response.data[i].barcode;
                    expiresDate = response.data[i].expirationdate;

                    // Search in the cache first.
                    if (elBarcode in $scope.cache) {
                        item = $scope.cache[elBarcode];
                        $scope.newList.push(item);
                    } else {
                        logService.debug('inventoryController', 'REST call for barcode ' + elBarcode);

                        restService.searchBarcode(elBarcode, function success(response) {
                            var product = response.data.product,
                                barcode = response.data.code,
                                item = {
                                    name: product.product_name,
                                    image: product.image_front_thumb_url,
                                    expires: expiresDate,
                                    barcode: barcode
                                };

                            $scope.newList.push(item);
                            $scope.cache[barcode] = item;

                        }, function error(response) {
                            $rootScope.addAlert(SEVERITY.WARNING, "Something went wrong and the latest inventory could not be found.");
                        });
                    }
                }

                $scope.$watch('newList', function(n) {
                    if (n.length === maxLength) {
                        if (!$scope.isInventoryEqual()) {
                            $scope.latest = $scope.newList;
                        }
                    }
                }, true);
            }, function error(response) {
                // TODO: Add in function
            });

            restService.getInventory(function success(response) {
                    $scope.newInventory = [];

                    var item,
                        index,
                        barcode,
                        product;

                    for (item in response.data) {
                        index = $scope.inventory.indexOf(response.data[item]);

                        if (index < 0) {
                            barcode = response.data[item].barcode;

                            // Search in the cache first.
                            if (barcode in $scope.cache) {
                                product = $scope.cache[barcode].name;
                            } else {
                                logService.debug('inventoryController', 'REST call for barcode ' + barcode);
                                restService.searchBarcode(barcode, function success(response) {
                                    var barcode = response.data.code,
                                        product = response.data.product.product_name;

                                    $scope.cache[barcode] = response.data;
                                    $scope.newInventory.push(product);

                                    $rootScope.addAlert(0, product + " was added to the inventory.");
                                }, function error(response) {
                                    $rootScope.addAlert(SEVERITY.WARNING, "Something went wrong and the latest inventory could not be found.");
                                });
                            }
                        }
                    }
                    $scope.inventory = $scope.newInventory;
                }),
                function error(response) {
                    // TODO: Add in function
                };
        }

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

            return equal
        }

        $scope.load();

        // Register event handlers
        $rootScope.$on("refreshInventory", function() {
            $scope.load();
        });

        // Cleanup
        $scope.$on("$destroy", function() {
            cache.setCache("inventoryController-inventory", $scope.cache);
            refreshDataService.unloadController('inventoryController');
        });
    }
]);
