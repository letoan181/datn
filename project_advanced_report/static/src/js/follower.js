odoo.define('project_advanced_report.project_follower', function (require) {
    "use strict";
    var MailFollowers = require('mail.Followers');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    var session = require('web.session');
    MailFollowers.include({
        _messageUnsubscribe: function (ids) {
            return this._rpc({
                model: this.model,
                method: 'message_unsubscribe',
                args: [[this.res_id], ids.partner_ids, ids.channel_ids],
            }).then(function () {
                // start logan
                // check if current user in ids.partner_ids
                var is_current_user_in_list = false;
                if (session.partner_id && ids.partner_ids && ids.partner_ids.length > 0) {
                    for (var i = 0; i < ids.partner_ids.length; i++) {
                        if (ids.partner_ids[i] == session.partner_id) {
                            is_current_user_in_list = true;
                        }
                    }
                }
                if (this.model == 'project.project' && is_current_user_in_list) {
                    this.do_action({
                        name: 'Projects',
                        type: 'ir.actions.act_window',
                        res_model: 'project.project',
                        views: [[false, 'kanban'], [false, 'form']],
                        target: 'main'
                    })
                } else {
                    this._reload.bind(this)
                }
                // end logan
            }.bind(this));
        },
    });
    return MailFollowers;
});