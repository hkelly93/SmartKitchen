/*jshint esversion: 6 */

/**
 * Used for i18n localization.
 * @param  {String} 'messagesService' The name of the AngularJS service
 * @param  {Function} function($sce   AngularJS functions
 * @return {Object}                   JavaScript object for translating messages
 */
app.factory('messagesService', function($sce) {

    const messages = {
        // English translations
        en: {
            SMART_KITCHEN: '<strong>Smart</strong>Kitchen',
            INVENTORY: 'Inventory',
            HELP: 'Help',
            ABOUT: 'About',
            SLOGAN: 'The future of<br/>kichens begins<br/>here.',
            READ_MORE: 'Read More',
            KITCHEN_HEALTH: 'Kitchen Health',
            FRIDGE: 'Fridge',
            NETWORK: 'Network',
            SCANNER: 'Scanner',
            LATEST_INVENTORY: 'Latest Inventory',
            NAME: 'Name',
            EXPIRATION_DATE: 'Expiration Date',
            EDIT: 'EDIT',
            DELETE: 'DELETE',
            INFO: 'INFO',
            WARNING: 'WARNING',
            CRITICAL: 'CRITICAL',
            UNKNOWN: 'UNKNOWN'
        },
        // Spanish translations
        es: {
            SMART_KITCHEN: '<strong>Cocina</strong>Inteligente',
            INVENTORY: 'Inventario',
            HELP: 'Ayuda',
            ABOUT: 'Unos',
            SLOGAN: 'El futuro de<br/>cocinas esta<br/>aqui.',
            READ_MORE: 'Lee Mas',
            KITCHEN_HEALTH: 'La salud de la cocina',
            FRIDGE: 'Refrigerador',
            NETWORK: 'Red',
            SCANNER: 'Escaner',
            LATEST_INVENTORY: 'Ultimo Inventario',
            NAME: 'Nombre',
            EXPIRATION_DATE: 'Fecha de caducidad',
            EDIT: 'EDITAR',
            DELETE: 'BORRAR',
            INFO: 'INFORMACION',
            WARNING: 'ADVERTENCIA',
            CRITICAL: 'CRITICO',
            UNKNOWN: 'DESCONOCIDO'
        },
        // French translations
        fr: {
            SMART_KITCHEN: '<strong>Cuisine</strong>Intelligente',
            INVENTORY: 'Inventaire',
            HELP: 'Assistance',
            ABOUT: 'Sur',
            SLOGAN: "L'avenir de la<br />cuisine commence<br />ici.",
            READ_MORE: 'Lire la suite',
            KITCHEN_HEALTH: 'La sante de la cuisine',
            FRIDGE: 'Frigo',
            NETWORK: 'Reseau',
            SCANNER: 'Scanner',
            LATEST_INVENTORY: 'Dernier Inventaire',
            NAME: 'Nom',
            EXPIRATION_DATE: "Date d'expiration",
            EDIT: 'EDITER',
            DELETE: 'EFFACER',
            INFO: 'INFORMATION',
            WARNING: 'ATTENTION',
            CRITICAL: 'CRUCIAL',
            UNKNOWN: 'INCONNU',
        }
    };

    /**
     * Gets the current locale language of the browser.
     * @return {[type]} [description]
     */
    getLocale = function() {
        var nav = window.navigator;
        return (nav.language === undefined) ? nav.userLanguage.split('-')[0] : nav.language.split('-')[0];

    };

    return {
        get: function(text) {
            switch (getLocale()) {
                case 'en':
                    return messages.en[text];
                case 'fr':
                    return messages.fr[text];
                case 'es':
                    return messages.es[text];
                default:
                    return messages.en[text];
            }
        },
        getHtml: function(text) {
            switch (getLocale()) {
                case 'en':
                    return $sce.trustAsHtml(messages.en[text]);
                case 'fr':
                    return $sce.trustAsHtml(messages.fr[text]);
                case 'es':
                    return $sce.trustAsHtml(messages.es[text]);
                default:
                    return $sce.trustAsHtml(messages.en[text]);
            }
        }
    };
});