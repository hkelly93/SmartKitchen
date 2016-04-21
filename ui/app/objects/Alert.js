/**
 * Create an Alert class to handle creating alerts
 * @param severity {Number} The severity of the alert.
 * @param message {String} The message for the alert.
 * @constructor
 */
function Alert(severity, message) {
    this.severity = severity;
    this.message = message;
    this.date = new Date();
}

/**
 * Returns the severity of the alert.
 * @return {Number}
 */
Alert.prototype.getSeverity = function () {
    return this.severity;
};

/**
 * Set the severity of the alert.
 * @param severity {Number} The severity to set.
 */
Alert.prototype.setSeverity = function (severity) {
    this.severity = severity;
};

/**
 * Returns the message of the alert.
 * @returns {String}
 */
Alert.prototype.getMessage = function () {
    return this.message;
};

/**
 * Sets the message of the alert.
 * @param message {String} The message to set.
 */
Alert.prototype.setMessage = function (message) {
    this.message = message;
};

/**
 * Returns the date of the alert.
 * @returns {Date}
 */
Alert.prototype.getDate = function () {
    return this.date;
};

/**
 * Sets the date of the message.
 * @param date {Date} The date to set.
 */
Alert.prototype.setDate = function (date) {
    this.date = date;
};