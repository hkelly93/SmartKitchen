/*jshint esversion: 6 */
/**
 * Main controller for the application. Contains loading/unloading functions
 * and refreshing functions.
 * @param  {String} 'mainController' Controller name
 * @param  {function} AngularJS services
 * @return {null}
 */
app.controller('mainController', ['$scope', '$rootScope', '$sce', '$parse', 'refreshData', 'logService', 'messagesService', 'restService', 'SEVERITY',
    function($scope, $rootScope, $sce, $parse, refreshData, logService, messagesService, restService, SEVERITY) {
        logService.setLevel(logService.LEVEL.WARNING);

        $scope.alertList = [];
        $scope.alertsVisible = false;
        $scope.showPopup = false;
        $scope.popupObject = {};
        $scope.latestRefresh = new Date().toLocaleString().replace(",", "");
        $scope.messages = messagesService.get;
        $scope.htmlMessages = messagesService.getHtml;
        $scope.popupDateChange = false;

        /**
         * Gets the running alerts from a REST call to open json/alerts.json. Also
         * sets the alert indicator in the navigation menu with the color of the
         * most severe alert.
         *
         * TODO: Replace json/alerts.json with the results of a REST call when it
         * is implemented.
         * @return {null}
         */
        $rootScope.addAlert = function(alertSeverity, alertMessage) {
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
                if ($scope.alertList[alert].severity == newAlert.severity && $scope.alertList[alert].message == newAlert.message) {
                    // Update the date and return.
                    alert.date = newAlert.date;
                    return;
                }
            }

            $scope.alertList.push(newAlert);

            createAlertSvg();
        };

        $scope.removeAlert = function(alert) {
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
                color = "";

            if ($scope.alertList.length === 0) {
                $scope.alerts = "";
                return;
            }

            for (var i = 0; i < $scope.alertList.length; i++) {
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
         * @param  {Int} count The number of alarms to display
         * @return {String} The svg element to add to the page
         */
        function generateAlertSvg(color, count) {
            var message = (count == 'X') ? count : '+' + count;
            var left = 0;

            if (count === 'X') {
                left = 7;
            } else if (parseInt(count) < 10) {
                left = 3;
            }

            var circle = '<circle cx="10" cy="10" r="10" fill="' + color + '" />';
            var text = '<text x="' + left + '" y="14" style="font-weight: 700;font-size: 8pt" >' + message + '</text>';
            var svg = '<svg width="25" height="25">' + circle + text + '</svg>';
            return svg;
        }

        $scope.showAlerts = function() {
            $scope.alertsVisible = !$scope.alertsVisible;

            if ($scope.alertsVisible) {
                $scope.alerts = $sce.trustAsHtml(generateAlertSvg("#e74c3c", 'X'));
            } else {
                createAlertSvg();
            }
        };

        $scope.togglePopup = function(item, submit) {
            if (submit !== undefined) {
                // Verify that there was a change.
                if ($scope.popupDateChange) {
                    var promise = restService.setExpirationDate(item);
                    promise.success(function(response) {
                        // Refresh the inventory.
                        $rootScope.$emit('refreshInventory', {});
                    });

                    promise.error(function(response) {
                        $rootScope.addAlert(SEVERITY.WARNING, 'Could not update the expiration date for ' + item.name);
                    });
                }
            }

            $scope.popupObject = (item === undefined) ? {} : angular.copy(item);
            $scope.showPopup = !$scope.showPopup;
        };

        $scope.dateChange = function() {
            $scope.popupDateChange = !$scope.popupDateChange;
        };

        // Register event handlers
        $rootScope.$on("refreshDateUpdate", function(event, message) {
            var date = message.date;
            $scope.latestRefresh = date.toLocaleString().replace(",", "");
        });
    }
]);