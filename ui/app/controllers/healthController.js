/*jshint esversion: 6 */
/**
 * Controls the kitchen health and refreshes the data.
 * @param  {String} 'healthController' Controller name
 * @param  {function} AngularJS services
 * @return {null}
 */
app.controller('healthController', ['$scope', '$rootScope', '$sce', 'refreshData', 'restService', 'SEVERITY', 'STATUS',
    function ($scope, $rootScope, $sce, refreshData, restService, SEVERITY, STATUS) {
        'use strict';

        // Add this controller to the loaded controllers and begin refreshing the data.
        refreshData.loadController('healthController');
        refreshData.refreshData('healthController', 'Refreshing health data.');

        $rootScope.$on("refreshNavigation", function () {
            $scope.load();
        });

        $scope.$on('$destroy', function () {
            refreshData.unloadController('healthController');
        });

        $scope.health = {
            fridge: generateHealthSvg(null),
            scanner: generateHealthSvg(null),
            network: generateHealthSvg(null)
        };

        /**
         * Load the data from the controller into the view.
         */
        $scope.load = function () {
            var fridgeHealthPromise = restService.getFridgeHealth();

            $rootScope.toggleHealthLoading(true);

            fridgeHealthPromise.success(function (response) {
                if (response.data !== STATUS.HEALTHY) {
                    $rootScope.addAlert(SEVERITY.WARNING, "Fridge health is " + response.data);
                }

                $scope.health.fridge = generateHealthSvg(response.data);
                $rootScope.toggleHealthLoading(false);
            });

            fridgeHealthPromise.error(function (response) {
                $scope.health.fridge = generateHealthSvg(null);
                $rootScope.addAlert(SEVERITY.CRITICAL, response.data);
                $rootScope.toggleHealthLoading(false);
            });

            $rootScope.toggleHealthLoading(true);
            var networkHealthPromise = restService.getNetworkHealth();

            networkHealthPromise.success(function (response) {
                if (response.data !== STATUS.HEALTHY) {
                    $rootScope.addAlert(SEVERITY.WARNING, "Network health is " + response.data);
                }
                $scope.health.network = generateHealthSvg(response.data);
                $rootScope.toggleHealthLoading(false);
            });

            networkHealthPromise.error(function (response) {
                $scope.health.network = generateHealthSvg(null);
                $rootScope.addAlert(SEVERITY.CRITICAL, response.data);
                $rootScope.toggleHealthLoading(false);
            });

            $rootScope.toggleHealthLoading(true);
            var scannerHealthPromise = restService.getNetworkHealth();

            scannerHealthPromise.success(function (response) {
                if (response.data !== STATUS.HEALTHY) {
                    $rootScope.addAlert(SEVERITY.WARNING, "Scanner health is " + response.data);
                }
                $scope.health.scanner = generateHealthSvg(response.data);
                $rootScope.toggleHealthLoading(false);
            });

            scannerHealthPromise.error(function (response) {
                $scope.health.scanner = generateHealthSvg(null);
                $rootScope.addAlert(SEVERITY.CRITICAL, response.data);
                $rootScope.toggleHealthLoading(false);
            });
        };

        /**
         * Generates the health svg circle with the correct color
         * @param  {String} severity the severity of the health
         * @return {String} The svg element to add to the page
         */
        function generateHealthSvg(severity) {
            var dangerColor = '#e74c3c',
                warningColor = '#f1c40f',
                healthyColor = '#2ecc71',
                color = '',
                sev,
                svg;

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

            sev = '<circle cx="10" cy="10" r="8" fill="' + color + '" />';
            svg = '<svg width="20" height="20">' + sev + '</svg>';
            return $sce.trustAsHtml(svg);
        }

        $scope.load();
    }
]);