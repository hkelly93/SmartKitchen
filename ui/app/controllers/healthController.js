/*jshint esversion: 6 */
/**
 * Controls the kitchen health and refreshes the data.
 * @param  {String} 'healthController' Controller name
 * @param  {function} AngularJS services
 * @return {null}
 */
app.controller('healthController', ['$scope', '$rootScope', '$sce', 'refreshData', 'restService', 'SEVERITY', 'STATUS',
    function($scope, $rootScope, $sce, refreshData, restService, SEVERITY, STATUS) {
        'use strict';

        // Add this controller to the loaded controllers and begin refreshing the data.
        refreshData.loadController('healthController');
        refreshData.refreshData('healthController', 'Refreshing health data.');

        $rootScope.$on("refreshNavigation", function() {
            $scope.load();
        });

        $scope.$on('$destroy', function() {
            refreshDataService.unloadController('healthController');
        });

        $scope.health = {
            fridge: generateHealthSvg(),
            scanner: generateHealthSvg(),
            network: generateHealthSvg()
        };

        /**
         * Load the data from the controller into the view.
         * @return {null}
         */
        $scope.load = function() {
            var fridgeHealthPromise = restService.getFridgeHealth();

            fridgeHealthPromise.success(function(response) {
                if (response.data !== STATUS.HEALTHY) {
                    $rootScope.addAlert(SEVERITY.WARNING, "Fridge health is " + response.data);
                }

                $scope.health.fridge = generateHealthSvg(response.data);
            });

            fridgeHealthPromise.error(function(response) {
                $scope.health.fridge = generateHealthSvg();
                $rootScope.addAlert(SEVERITY.CRITICAL, response.data);
            });

            var networkHealthPromise = restService.getNetworkHealth();

            networkHealthPromise.success(function(response) {
                if (response.data !== STATUS.HEALTHY) {
                    $rootScope.addAlert(SEVERITY.WARNING, "Network health is " + response.data);
                }
                $scope.health.network = generateHealthSvg(response.data);
            });

            networkHealthPromise.error(function(response) {
                $scope.health.network = generateHealthSvg();
                $rootScope.addAlert(SEVERITY.CRITICAL, response.data);
            });

            var scannerHealthPromise = restService.getScannerHealth();

            scannerHealthPromise.success(function(response) {
                if (response.data !== STATUS.HEALTHY) {
                    $rootScope.addAlert(SEVERITY.WARNING, "Scanner health is " + response.data);
                }
                $scope.health.scanner = generateHealthSvg(response.data);
            });

            scannerHealthPromise.error(function(response) {
                $scope.health.scanner = generateHealthSvg();
                $rootScope.addAlert(SEVERITY.CRITICAL, response.data);
            });
        };

        /**
         * Generates the health svg circle with the correct color
         * @param  {String} the severity of the health
         * @return {String} The svg element to add to the page
         */
        function generateHealthSvg(severity) {
            var dangerColor = '#e74c3c',
                warningColor = '#f1c40f',
                healthyColor = '#2ecc71';

            var color = '';

            switch (severity) {
                case STATUS.HEALTHY:
                    color = healthyColor;
                    break;
                case STATUS.WARNING:
                case STATUS.WEAK:
                    color = warningColor;
                    break;
                case STATUS.CRITICAL:
                    color = dangerColor;
                    break;
                default:
                    color = "#BEBEBE";
                    break;
            }
            var sev = '<circle cx="10" cy="10" r="8" fill="' + color + '" />';
            var svg = '<svg width="20" height="20">' + sev + '</svg>';
            return $sce.trustAsHtml(svg);
        }

        $scope.load();
    }
]);