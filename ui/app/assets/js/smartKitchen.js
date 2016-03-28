(function() {
    app = angular.module("smartKitchen", ['ngAnimate']);

    // Enum for alert severities.
    app.constant('SEVERITY', {
        INFO: 0,
        WARNING: 1,
        CRITICAL: 2
    });

    // Enum for system status.
    app.constant('STATUS', {
        HEALTHY: 'healthy',
        WARNING: 'warning',
        CRITICAL: 'critical'
    });

})();
