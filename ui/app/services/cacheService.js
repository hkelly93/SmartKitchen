app.factory('cache', [function() {
    return {
        /**
         * Caches an object in local storage.
         * @param  {String} name The name of the object.
         * @param  {Object} obj  The Javascript object to cache.
         * @return {null}
         */
        setCache: function(name, obj) {
            if (typeof(Storage) !== "undefined") {
                if (obj !== undefined) {
                    obj.date = +new Date();
                }

                localStorage.setItem(name, JSON.stringify(obj));
            }
        },

        /**
         * Gets an object from local storage.
         * @param  {String} name The name of the object that was stored.
         * @return {Object}      The object that was cached.
         */
        getCache: function(name) {
            if (typeof(Storage) !== "undefined") {
                var obj = localStorage.getItem(name);

                // if (obj !== undefined && obj.date !== undefined) {
                //     var date = new Date();
                //     date.setDate(date.getDate() - 5); // Five days ago.
                //
                //     var cacheDate = new Date(parseInt(JSON.parse(obj)));
                //     if (cacheDate < date) {
                //         return {};
                //     }
                // }
                return (obj === null) ? {} : JSON.parse(obj);
            }
            return {};
        }
    };
}]);
