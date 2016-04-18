/*jshint esversion: 6 */
/**
 * Main controller for the application. Contains loading/unloading functions
 * and refreshing functions.
 * @param  {String} 'mainController' Controller name
 * @param  {function} AngularJS services
 * @return {null}
 */
app.controller('mainController', ['$scope', '$rootScope', '$sce', '$parse', '$timeout', 'refreshData', 'logService', 'messagesService', 'restService', 'SEVERITY',
    function ($scope, $rootScope, $sce, $parse, $timeout, refreshData, logService, messagesService, restService, SEVERITY) {
        'use strict';

        logService.setLevel(logService.LEVEL.WARNING);

        $scope.alertList = [];
        $scope.alertsVisible = false;
        $scope.showPopup = false;
        $scope.popupObject = {};
        $scope.latestRefresh = new Date().toLocaleString().replace(",", "");
        $scope.messages = messagesService.get;
        $scope.htmlMessages = messagesService.getHtml;
        $scope.popupDateChange = false;

        $rootScope.inventoryLoading = 0;
        $rootScope.toggleInventoryBusy = function (enable) {
            if (enable) {
                $rootScope.inventoryLoading += 1;
            } else {
                if ($rootScope.inventoryLoading <= 1) {
                    $timeout(function () {
                        $rootScope.inventoryLoading = 0;
                    }, 2000);
                } else {
                    $rootScope.inventoryLoading -= 1;
                }
            }
        };

        $rootScope.healthLoading = 0;
        $rootScope.toggleHealthLoading = function (enable) {
            if (enable) {
                $rootScope.healthLoading += 1;
            } else {
                if ($rootScope.healthLoading <= 1) {
                    $timeout(function () {
                        $rootScope.healthLoading = 0;
                    }, 2000);
                } else {
                    $rootScope.healthLoading -= 1;
                }
            }
        };

        $rootScope.busy = 0;
        $rootScope.toggleBusy = function (enable) {
            $timeout(function () {
                if (enable) {
                    $rootScope.busy += 1;
                } else {
                    $rootScope.busy -= 1;

                    if ($rootScope.busy < 0) {
                        $rootScope.busy = 0;
                    }
                }
            }, 4000);
        };

        /**
         * Gets the running alerts from a REST call to open json/alerts.json. Also
         * sets the alert indicator in the navigation menu with the color of the
         * most severe alert.
         */
        $rootScope.addAlert = function (alertSeverity, alertMessage) {
            switch (alertSeverity) {
                case 0:
                    alertMessage = "[" + $scope.messages('INFO') + "] " + alertMessage;
                    break;
                case 1:
                    alertMessage = "[" + $scope.messages('WARNING') + "] " + alertMessage;
                    break;
                case 2:
                    alertMessage = "[" + $scope.messages('CRITICAL') + "] " + alertMessage;
                    break;
                default:
                    alertMessage = "[" + $scope.messages('UNKNOWN') + "] " + alertMessage;
                    break;
            }

            var newAlert = {
                severity: alertSeverity,
                message: alertMessage,
                date: new Date()
            };

            for (var alert in $scope.alertList) {
                // Check for duplicates.
                if ($scope.alertList[alert].severity === newAlert.severity && $scope.alertList[alert].message === newAlert.message) {
                    // Update the date and return.
                    $scope.alertList[alert].date = newAlert.date;
                    break;
                }
            }

            $scope.alertList.push(newAlert);

            createAlertSvg();
        };

        $scope.removeAlert = function (alert) {
            var index = $scope.alertList.indexOf(alert);
            if (index > -1) {
                $scope.alertList.splice(index, 1);
            } else {
                $rootScope.addAlert(SEVERITY.WARNING, "Could not remove alert.");
            }

            if ($scope.alertList.length === 0) {
                $scope.alertsVisible = false;
                $scope.alerts = "";
            }
        };

        function createAlertSvg() {
            var maxSeverity = 0,
                color = "",
                i = 0;

            if ($scope.alertList.length === 0) {
                $scope.alerts = "";
                return;
            }

            for (i; i < $scope.alertList.length; i++) {
                if ($scope.alertList[i].severity > maxSeverity) {
                    maxSeverity = $scope.alertList[i].severity;
                }
            }

            switch (maxSeverity) {
                case 0:
                    color = "#2ecc71";
                    break;
                case 1:
                    color = "#f1c40f";
                    break;
                case 2:
                    color = "#e74c3c";
                    break;
            }

            var svg = generateAlertSvg(color, $scope.alertList.length);
            $scope.alerts = $sce.trustAsHtml(svg);
        }

        /**
         * Generates the alert svg circle with the correct color and alert count.
         * @param  {String} color The HEX color for the circle
         * @param  {Number} count The number of alarms to display
         * @return {String} The svg element to add to the page
         */
        function generateAlertSvg(color, count) {
            var message = (count == 'X') ? count : '+' + count;
            var left = 0;

            if (count == 'X') {
                left = 7;
            } else if (parseInt(count) < 10) {
                left = 3;
            }

            var circle = '<circle cx="10" cy="10" r="10" fill="' + color + '" />';
            var text = '<text x="' + left + '" y="14" style="font-weight: 700;font-size: 8pt;" >' + message + '</text>';
            return '<svg width="25" height="25">' + circle + text + '</svg>';
        }

        $scope.showAlerts = function () {
            $scope.alertsVisible = !$scope.alertsVisible;

            if ($scope.alertsVisible) {
                $scope.alerts = $sce.trustAsHtml(generateAlertSvg("#e74c3c", 'X'));
            } else {
                createAlertSvg();
            }
        };

        $scope.togglePopup = function (item, submit) {
            if (submit !== undefined) {
                $rootScope.toggleBusy(true);
                var promise = restService.setExpirationDate(item);
                promise.success(function (response) {
                    // Refresh the inventory.
                    $rootScope.$emit('refreshInventory', {});
                    $rootScope.toggleBusy(false);

                    $scope.popupObject = {};
                });

                promise.error(function (response) {
                    $rootScope.toggleBusy(false);
                    $rootScope.addAlert(SEVERITY.WARNING, 'Could not update the expiration date for ' + item.name);

                    $scope.popupObject = {};
                });
            }

            $scope.popupObject = (item === undefined) ? {} : angular.copy(item);
            $scope.showPopup = !$scope.showPopup;
        };

        // Register event handlers
        $rootScope.$on("refreshDateUpdate", function (event, message) {
            var date = message.date;
            $scope.latestRefresh = date.toLocaleString().replace(",", "");
        });
    }
]);