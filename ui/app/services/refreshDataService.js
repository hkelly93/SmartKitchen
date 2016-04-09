/* jshint esversion: 6 */

app.factory('refreshData', ['$rootScope', '$interval', 'logService',
    function($rootScope, $interval, logService) {
        var loadedControllers = [], // List of controllers currently loaded.
            refreshingControllers = [], // List of controllers that are doing a refresh.
            latestRefresh = new Date(); // The last time the data was refreshed.

        const refresh = true, // Whether or not to refresh the data.
            refreshRate = 5; // in seconds.

        return {
            /**
             * Load a controller into the application. This allows for a controller to
             * be refreshed automatically by the refreshData service.
             * @param  {String} controllerName The name of the controller that is being loaded.
             * @return {null}
             */
            loadController: function(controllerName) {
                logService.debug('refreshDataService', 'Loading ' + controllerName + '.');

                if (loadedControllers.indexOf(controllerName) > -1) {
                    logService.warning('refreshDataService', controllerName + " was already loaded and will not be loaded again.");
                    return;
                }

                loadedControllers.push(controllerName);
            },
            /**
             * Unload a controller from the application to prevent automatic refreshing.
             * @param  {String} controllerName The name of the controller that is being unloaded.
             * @return {[type]}                [description]
             */
            unloadController: function(controllerName) {
                logService.debug('refreshDataService', 'Unloading ' + controllerName + '.');
                var index = loadedControllers.indexOf(controllerName);
                if (index !== undefined && index > -1) {
                    loadedControllers.splice(index, 1);
                }

                this.removeRefreshing(controllerName);
            },
            /**
             * Refreshes the controller's data if it is not already refreshing.
             * @param  {String} controller The name of the controller to refresh.
             * @param  {String} log        A log message from the controller.
             * @return {null}
             */
            refreshData: function(controller, log) {
                timer = $interval(function() {
                    var isLoaded = function(controllerName) {
                        return loadedControllers.indexOf(controllerName) > -1;
                    };

                    var setRefreshing = function(controllerName) {
                        refreshingControllers.push(controllerName);
                    };

                    var removeRefreshing = function(controllerName) {
                        index = refreshingControllers.indexOf(controllerName);
                        if (index !== undefined && index > -1) {
                            refreshingControllers.splice(index, 1);
                        }
                    };

                    var isRefreshing = function(controllerName) {
                        return refreshingControllers.indexOf(controllerName) > -1;
                    };

                    if (!refresh) return;

                    var event = '',
                        isRunning = isRefreshing(controller),
                        loaded = isLoaded(controller);

                    switch (controller) {
                        case 'navController':
                            event = 'refreshNavigation';
                            break;
                        case 'healthController':
                            event = 'refreshHealth';
                            break;
                        case 'inventoryController':
                            event = 'refreshInventory';
                            break;
                        default:
                            return;
                    }

                    setRefreshing(controller);

                    logService.info('refreshDataService', log);
                    $rootScope.$emit(event, {});
                    $rootScope.$emit('refreshDateUpdate', {
                        'date': new Date()
                    });

                    removeRefreshing(controller);
                }, refreshRate * 1000);

                // Cleanup
                $rootScope.$on("$destroy", function() {
                    if (timer) {
                        $timeout.cancel(timer);
                    }
                });
            }
        };
    }
]);