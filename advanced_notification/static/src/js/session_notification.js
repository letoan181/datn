var global_notification_is_first_time = true;
odoo.define('advanced.notification', function (require) {
    "use strict";
    var Notification = require('web.Notification');
    var FireworkEffect = require('web.FireWork');
    var session = require('web.session');
    var WebClient = require('web.WebClient');
    var RecurrentNotification = Notification.extend({
        template: "RecurrentNotification",
        xmlDependencies: (Notification.prototype.xmlDependencies || [])
            .concat(['/advanced_notification/static/src/xml/template.xml']),
        init: function (parent, params) {
            this._super(parent, params);
            this.sticky = true;
            this.events = _.extend(this.events || {}, {
                'click .link2recall': function () {
                    this.close();
                },
            });
        },
    });
    WebClient.include({
        show_application: function () {
            var self = this;
            // return this._super.apply(this, arguments).then(this.display_recurrent_notify.bind(this));
            return this._super.apply(this, arguments)
        },
        display_recurrent_notify: function () {
            var notifications = {
                'title': 'Reminder',
                'message': 'Rửa tay thường xuyên: khi đến, khi chấm công, trước và sau khi ăn, khi ho, hắt hơi, khi tiếp xúc, khi đi vệ sinh'
            };
            var self = this;
            // var notification = false;
            // Clear previously set timeouts and destroy currently displayed recurrent notifications
            clearTimeout(this.get_next_recurrent_notif_timeout);
            _.each(this.recurrent_notif_timeouts, clearTimeout);
            var distance = 0
            if (global_notification_is_first_time) {
                global_notification_is_first_time = false
            } else {
                distance = this.get_distance_time_now();
            }
            self.recurrent_notif_timeouts = {};
            if (self.recurrent_notif == undefined || !Number.isInteger(self.recurrent_notif)) {
                self.recurrent_notif_timeouts = setTimeout(function () {
                    var notificationID = self.call('notification', 'notify', {
                        Notification: RecurrentNotification,
                        title: notifications.title,
                        message: notifications.message,
                        onClose: function () {
                            delete self.recurrent_notif;
                        },
                    });
                    self.recurrent_notif = notificationID;

                }, distance);
                // notification =  true;
            }
            distance = this.get_distance_time_now();
            this.get_next_recurrent_notif_timeout = setTimeout(this.get_next_recurrent_notify.bind(this), distance);
        },
        display_firework_effect: function () {
            var self = this;
            this._rpc({
                model: 'res.users',
                method: 'check_last_session',
                args: [],
            }).then(function (result) {
                if (result) {
                    new FireworkEffect({
                        title: 'HappyBirthday ' + session.name,
                        message: 'Best wishes to you.'
                    }).appendTo(self.$el);
                }
            });
        },
        get_next_recurrent_notify: function () {
            this.display_recurrent_notify()
        },
        get_distance_time_now: function () {
            var now = new Date();
            var time_now = now.getHours() + now.getMinutes() / 60;
            var distance = 0
            if (time_now < 8.0) {
                distance = 8.0 - time_now;
            } else if (8.0 < time_now < 11.25) {
                distance = 11.25 - time_now;
            } else if (11.25 < time_now < 13.0) {
                distance = 13.0 - time_now;
            } else if (13.0 < time_now < 16.75) {
                distance = 16.75 - time_now;
            } else {
                // var distance = 10;
                distance = 15;
            }
            distance = Math.abs(distance)
            return distance * 3600 * 1000
        }
    });
});