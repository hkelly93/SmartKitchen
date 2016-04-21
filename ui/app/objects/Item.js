/**
 * Create an Item class to be used in the inventory.
 * @param uuid {String} The uuid of the Item object
 * @constructor
 */
function Item(uuid) {
    this.name = '';
    this.image = '';
    this.expires = '';
    this.expiresDate = '';
    this.barcode = '';
    this.uuid = uuid;
}

/**
 * Gets the name of the Item.
 * @returns {String}
 */
Item.prototype.getName = function () {
    return this.name;
};

/**
 * Sets the name of the Item.
 * @param name {String} The name to set.
 */
Item.prototype.setName = function (name) {
    this.name = name;
};

/**
 * Gets the image of the item.
 * @returns {String}
 */
Item.prototype.getImage = function () {
    return this.image;
};

/**
 * Sets the image of the item.
 * @param image {String} The image to set.
 */
Item.prototype.setImage = function (image) {
    this.image = image;
};

/**
 * Gets the expiration date of the item.
 * @returns {String}
 */
Item.prototype.getExpires = function () {
    return this.expires;
};

/**
 * Sets the expiration date of the item.
 * @param expires {String} The expiration date to set.
 */
Item.prototype.setExpires = function (expires) {
    this.expires = expires;
};

/**
 * Gets the expires date of the item.
 * @returns {Date}
 */
Item.prototype.getExpiresDate = function () {
    return this.expiresDate;
};

/**
 * Sets the expires date of the item.
 * @param barcode {Date} The date to set.
 */
Item.prototype.setExpiresDate = function (date) {
    this.expiresDate = date;
};

/**
 * Gets the barcode of the item.
 * @returns {String}
 */
Item.prototype.getBarcode = function () {
    return this.barcode;
};

/**
 * Sets the barcode of the item.
 * @param barcode {String} The barcode to set.
 */
Item.prototype.setBarcode = function (barcode) {
    this.barcode = barcode;
};