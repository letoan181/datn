odoo.define('tracking.model.Message', function (require) {
    "use strict";

    var Message = require('mail.model.Message');

    Message.include({
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
        getTrackingAccessRight: function () {
            return this.TrackingAccessRight
        },
        init: function (parent, data, emojis) {
            this.TrackingAccessRight = data.tracking_access
            this._super.apply(this, arguments);

        },
    });
});
