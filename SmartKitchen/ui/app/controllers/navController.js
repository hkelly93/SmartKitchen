/**
 * Controls the navigation menu on the top of the application. Refreshes data
 * and controls getting and showering alerts.
 * @param  {String} 'navController'  Name of the controller
 * @param  {function} AngularJS services
 * @return {null}
 */
app.controller('navController', ['$scope', '$rootScope', 'refreshData', 'restService', 'SEVERITY',
    function($scope, $rootScope, refreshData, restService, SEVERITY) {
        // Add this controller to the list of loaded controllers
        refreshData.loadController('navController');
        refreshData.refreshData('navController', 'Refreshing navigation data.');

        $rootScope.$on("refreshNavigation", function() {
            $scope.load();
        });

        $scope.$on('$destroy', function() {
            refreshDataService.unloadController('navController');
        });

        /**
         * Load the data from the REST api.
         * @return {null}
         */
        $scope.load = function() {
            var promise = restService.getInventory();

            promise.success(function(response) {
                $scope.inventory = '(' + response.data.length + ')';
            });

            promise.error(function(response) {
                $scope.inventory = '(0)';
                $rootScope.addAlert(SEVERITY.CRITICAL, "Something went wrong and the inventory could not be found");
            });
        };

        $scope.load();
    }
]);
