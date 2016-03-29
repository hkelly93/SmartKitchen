/**
 * Logging service that logs messages in an easy to use way.
 * @param  {String} 'logService' The name of the service
 * @return {Object}              Javascript object for logging.
 */
app.factory('logService', function() {
    // What the current logging level is. The logger does not log anything that is
    // under the set level.
    var currentLevel = 0;

    return {
        /**
         * Logging levels.
         * @type {Object}
         */
        LEVEL: {
            DEBUG: 0,
            INFO: 1,
            WARNING: 2,
            CRITICAL: 3
        },
        /**
         * Sets the lowest level to log. Everything that gets logged under The
         * level is ignored.
         * @param  {LEVEL} logLevel Lowest level to log at
         * @return {null}
         */
        setLevel: function(logLevel) {
            switch (logLevel) {
                case this.LEVEL.DEBUG:
                    currentLevel = this.LEVEL.DEBUG;
                    break;
                case this.LEVEL.INFO:
                    currentLevel = this.LEVEL.INFO;
                    break;
                case this.LEVEL.WARNING:
                    currentLevel = this.LEVEL.WARNING;
                    break;
                case this.LEVEL.CRITICAL:
                    currentLevel = this.LEVEL.CRITICAL;
                    break;
                default:
                    currentLevel = this.LEVEL.INFO;
            }
        },
        /**
         * Log a debug message.
         * @param  {String} caller  The controller or service that is logging.
         * @param  {String} message The message to log.
         * @return {null}
         */
        debug: function(caller, message) {
            if (this.LEVEL.DEBUG >= currentLevel) {
                console.log("[DEBUG] [" + caller + "] " + message);
            }
        },
        /**
         * Log an info message.
         * @param  {String} caller  The controller or service that is logging.
         * @param  {String} message The message to log.
         * @return {null}
         */
        info: function(caller, message) {
            if (this.LEVEL.INFO >= currentLevel) {
                console.log("[INFO] [" + caller + "] " + message);
            }
        },
        /**
         * Log a warning message.
         * @param  {String} caller  The controller or service that is logging.
         * @param  {String} message The message to log.
         * @return {null}
         */
        warning: function(caller, message) {
            if (this.LEVEL.WARNING >= currentLevel) {
                console.log("[WARNING] [" + caller + "] " + message);
            }
        },
        /**
         * Log a critical message.
         * @param  {String} caller  The controller or service that is logging.
         * @param  {String} message The message to log.
         * @return {null}
         */
        critical: function(caller, message) {
            if (this.LEVEL.CRITICAL >= currentLevel) {
                console.log("[CRITICAL] [" + caller + "] " + message);
            }
        }
    }

});
