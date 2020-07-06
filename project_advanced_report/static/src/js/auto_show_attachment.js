odoo.define('Advanced.mail.Chatter', function (require) {
    var Activity = require('mail.Activity');
    var AttachmentBox = require('mail.AttachmentBox');
    var ChatterComposer = require('mail.composer.Chatter');
    var Dialog = require('web.Dialog');
    var Followers = require('mail.Followers');
    var ThreadField = require('mail.ThreadField');
    var mailUtils = require('mail.utils');

    var concurrency = require('web.concurrency');
    var config = require('web.config');
    var core = require('web.core');
    var Widget = require('web.Widget');

    var _t = core._t;
    var QWeb = core.qweb;
    var Chater = require('mail.Chatter')
    Chater.include({
        // template: 'mail.Chatter',
        // custom_events: {
        //     delete_attachment: '_onDeleteAttachment',
        //     discard_record_changes: '_onDiscardRecordChanges',
        //     reload_attachment_box: '_onReloadAttachmentBox',
        //     reload_mail_fields: '_onReloadMailFields',
        // },
        // events: {
        //     'click .o_chatter_button_new_message': '_onOpenComposerMessage',
        //     'click .o_chatter_button_log_note': '_onOpenComposerNote',
        //     'click .o_chatter_button_attachment': '_onClickAttachmentButton',
        //     'click .o_chatter_button_schedule_activity': '_onScheduleActivity',
        // },
        // supportedFieldTypes: ['one2many'],

        /**
         * @override
         * @param {widget} parent
         * @param {Object} record
         * @param {Object} mailFields
         * @param {string} [mailFields.mail_activity]
         * @param {string} [mailFields.mail_followers]
         * @param {string} [mailFields.mail_thread]
         * @param {Object} options
         * @param {string} [options.viewType=record.viewType] current viewType in
         *   which the chatter is instantiated
         */

        start: function () {
            if (this.context.default_model === 'project.task') {
                supper = this._super.apply(this, arguments);
                this._$topbar = this.$('.o_chatter_topbar');
                var fieldDefs = _.invoke(this.fields, 'appendTo', $('<div>'));
                var def = this._dp.add($.when.apply($, fieldDefs));
                this._render(def).then(this._updateMentionSuggestions.bind(this));
                this._render(def).then(this._onClickAttachmentButton.bind(this));
                // this.$el.removeClass('.o_chatter_button_new_message');
                this.$el.find('.o_chatter_button_new_message').hide();
                this.$el.find('.o_chatter_button_log_note').hide();
                console.log(document.body.innerHTML);
                this.fields.thread = false
                // $(document).find('.o_mail_thread').hide();
                return supper
            } else {
                this._super.apply(this, arguments);
            }

        },
    })
});