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

        /**
         * Load the data from the controller into the view.
         * @return {null}
         */
        $scope.load = function() {
            function success(response) {
                var element;
                // Check the health
                for (element in response.data) {
                    if (response.data[element] !== STATUS.HEALTHY) {
                        $rootScope.addAlert(SEVERITY.WARNING, element + " is not healthy.");
                    }
                }
                $scope.health = {
                    fridge: generateHealthSvg(response.data.fridge),
                    scanner: generateHealthSvg(response.data.scanner),
                    network: generateHealthSvg(response.data.network),
                };
            };

            function error(response) {
                $rootScope.addAlert(SEVERITY.CRITICAL, "Something went wrong and the kitchen health could not be processed.");
                $scope.health = {
                    fridge: generateHealthSvg(),
                    scanner: generateHealthSvg(),
                    network: generateHealthSvg()
                };
            }

            restService.getHealth(success, error);
        };

        /**
         * Generates the health svg circle with the correct color
         * @param  {String} the severity of the health
         * @return {String} The svg element to add to the page
         */
        function generateHealthSvg(severity) {
            const dangerColor = '#e74c3c',
                warningColor = '#f1c40f',
                healthyColor = '#2ecc71';

            var color = '';

            switch (severity) {
                case STATUS.HEALTHY:
                    color = healthyColor;
                    break;
                case STATUS.WARNING:
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
