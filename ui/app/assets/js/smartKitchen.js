(function() {
    app = angular.module("smartKitchen", ['ngAnimate']);

    // Used http://jsfiddle.net/3zhbB/6/ to figure this out.
    app.filter('array', function() {
        return function(arrayLength) {
            if (!arrayLength) return;
            arrayLength = Math.ceil(arrayLength);
            var arr = new Array(arrayLength),
                i = 0;
            for (; i < arrayLength; i++) {
                arr[i] = i;
            }
            return arr;
        };
    });

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
        CRITICAL: 'critical',
        WEAK: 'weak'
    });

})();