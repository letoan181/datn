odoo.define('web.FireWork', function (require) {
    "use strict";


    var Widget = require('web.Widget');
    var core = require('web.core');

    var _t = core._t;

    var FireworkEffect = Widget.extend({
        template: 'happyBirthday.effect',
        xmlDependencies: ['/advanced_notification/static/src/xml/template.xml'],
        jsLibs: [
            '/advanced_notification/static/lib/jquery.fireworks.js',
        ],
        /**
         * @override
         * @constructor
         */
        init: function (options) {
            this._super.apply(this, arguments);
            this.options = _.defaults(options || {}, {
                title: _t('HappyBirthday!'),
                message: _t('Best Wish'),
            });
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var $section = $('section').fireworks({
                sound: false, // sound effect
                opacity: 0.8,
                width: '100%',
                height: '100%'
            });
            this.$('.o_effect').append($section)
            // destroy  man when the user clicks outside
            setTimeout(function () {
                core.bus.on('click', self, function (ev) {
                    if (ev.originalEvent && ev.target.className.indexOf('o_effect') === -1) {
                        this.destroy();
                    }
                });
            }, 600);
            this.$('.message_title').append(this.options.title);
            this.$('.message').append(this.options.message);
            return this._super.apply(this, arguments);
        }
    });

    return FireworkEffect;
});
