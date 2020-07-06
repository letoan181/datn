odoo.define('web.statetest', function (require) {
    "use strict";
    var fields = require('web.basic_fields');
    var registry = require('web.field_registry');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var Widget = require('web.Widget');
    var widgetRegistry = require('web.widget_registry');
    var qweb = core.qweb;

    var _t = core._t;

    var StateTest = fields.InputField.extend({
        className: 'o_field_status',
        supportedFieldTypes: ['char'],

        /**
         * Urls are links in readonly mode.
         *
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.tagName = this.mode === 'readonly' ? 'div' : 'input';
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * Returns the associated link.
         *
         * @override
         */
        getFocusableElement: function () {
            return this.mode === 'readonly' ? this.$el : this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * In readonly, the widget needs to be a link with proper href and proper
         * support for the design, which is achieved by the added classes.
         *
         * @override
         * @private
         */
        _renderReadonly: function () {

            var renderTxt = 'Unfixed';
            var renderClass = 'grey';

            if (this.value == '0') {
                renderTxt = 'Fixed';
                renderClass = 'green';
            } else if (this.value == '1') {
                renderTxt = 'Wont fix';
                renderClass = 'red';


            } else if (this.value == '3') {
                renderTxt = 'Need further discussion';
                renderClass = 'orange';

            } else if (this.value == '4') {
                renderTxt = 'Can not reproduce';
                renderClass = 'purple';

            }
            this.$el.text(renderTxt)
                .addClass('o_form_uri o_text_overflow')
                .attr('data-target', '_blank')
                .attr('class', renderClass);
        }
    });

//viewRegistry.add('web.statetest', StateTest);

    registry.add('state_test', StateTest);

////////////////
    var TStateTest = fields.InputField.extend({
        className: 'o_field_status',
        supportedFieldTypes: ['char'],

        /**
         * Urls are links in readonly mode.
         *
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.tagName = this.mode === 'readonly' ? 'div' : 'input';
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * Returns the associated link.
         *
         * @override
         */
        getFocusableElement: function () {
            return this.mode === 'readonly' ? this.$el : this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * In readonly, the widget needs to be a link with proper href and proper
         * support for the design, which is achieved by the added classes.
         *
         * @override
         * @private
         */
        _renderReadonly: function () {

            var renderTxt = 'Untested';
            var renderClass = 'grey';
            if (this.value == '0') {
                renderTxt = 'Passed';
                renderClass = 'green'
            } else if (this.value == '1') {
                renderTxt = 'Failed';
                renderClass = 'red'


            } else if (this.value == '3') {
                renderTxt = 'Need further discussion';
                renderClass = 'orange'

            } else if (this.value == '4') {
                renderTxt = 'Can not reproduce';

            }
            this.$el.text(renderTxt)
                .addClass('o_form_uri o_text_overflow')
                .attr('data-target', '_blank')
                .attr('class', renderClass);
        }
    });

//viewRegistry.add('web.statetest', StateTest);

    registry.add('tester_state_test', TStateTest);

    return StateTest;

});


odoo.define('web.link_minimize', function (require) {
    "use strict";
    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');
    var LinkMinimize = AbstractField.extend({
        _render: function () {
            if (this.value) {
                this.$el.html('<a href="' + this.value + '" target="_blank">Open Image / Video In New Tab</a>');
            }
        }
    });
    field_registry.add('link_minimize', LinkMinimize);
});