// create notification on web browser
odoo.define('advanced.mail.Notification', function (require) {
    "use strict";
    var MailManager = require('mail.Manager');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;
    MailManager.include({
        _onNotification: function (notifs) {
            var self = this;
            notifs = this._filterNotificationsOnUnsubscribe(notifs);
            _.each(notifs, function (notif) {
                var model = notif[0][1];
                var object_title = '';
                if (model === 'ir.needaction') {
                    try {
                        if (notif[1]['model'] != false) {
                            $.when(
                                rpc.query({
                                    model: notif[1]['model'],
                                    method: 'search_read',
                                    args: [[['id', '=', notif[1]['res_id']]], ['name']]
                                }, {
                                    shadow: true,
                                }).then(function (data) {
                                    object_title = data[0]['name'];
                                })).then(function (result) {
                                var tmp = document.createElement("DIV");
                                tmp.innerHTML = notif[1]['body'];
                                var tmp_text = tmp.textContent || tmp.innerText || "";
                                if (tmp_text.length == 0) {
                                    tmp_text = notif[1]['subtype_description'] + '!\n';
                                    for (var i = 0; i < notif[1]['tracking_value_ids'].length; i++) {
                                        tmp_text += notif[1]['tracking_value_ids'][i]['changed_field'] + ' Updated: ' + notif[1]['tracking_value_ids'][i]['old_value'] + ' -> ' + notif[1]['tracking_value_ids'][i]['new_value'];
                                    }
                                }
                                tmp_text = 'Title: ' + object_title + '\n' + tmp_text;
                                if (notif[1]['model'] == 'project.task') {
                                    var notification = new Notification('Task ! ' + notif[1]['author_id'][1], {
                                        body: tmp_text,
                                        icon: "/advanced_mail/static/src/img/hi.gif"
                                    });
                                    notification.onclick = function () {
                                        window.focus();
                                        if (this.cancel) {
                                            this.cancel();
                                        } else if (this.close) {
                                            this.close();
                                        }
                                        self.do_action({
                                            type: 'ir.actions.act_window',
                                            res_model: 'project.task',
                                            res_id: notif[1]['res_id'],
                                            views: [[false, 'form']],
                                            target: 'current'
                                        })
                                    };
                                    self.do_notify(
                                        _t("Task Update From: ") + notif[1]['author_id'][1], tmp_text);
                                } else {
                                    var notification = new Notification('Action ! ' + notif[1]['author_id'][1], {
                                        body: tmp_text,
                                        icon: "/advanced_mail/static/src/img/hi.gif"
                                    });
                                    notification.onclick = function () {
                                        window.focus();
                                        if (this.cancel) {
                                            this.cancel();
                                        } else if (this.close) {
                                            this.close();
                                        }
                                        self.do_action({
                                            type: 'ir.actions.act_window',
                                            res_model: notif[1]['model'],
                                            res_id: notif[1]['res_id'],
                                            views: [[false, 'form']],
                                            target: 'current'
                                        })
                                    };
                                    self.do_notify(
                                        _t("Need Action From: ") + notif[1]['author_id'][1], tmp_text);
                                }
                            });
                        } else {
                            var tmp_text = notif[1]['subject'];
                            if (tmp_text.length > 0) {
                                var notification = new Notification('Action ! ' + notif[1]['author_id'][1], {
                                    body: tmp_text,
                                    icon: "/advanced_mail/static/src/img/hi.gif"
                                });
                                notification.onclick = function () {
                                    window.focus();
                                    if (this.cancel) {
                                        this.cancel();
                                    } else if (this.close) {
                                        this.close();
                                    }

                                    var text_body = notif[1]['body'];
                                    var i;
                                    var index_model = text_body.indexOf("model=");
                                    for (i = index_model; ; i++) {
                                        if (text_body[i] == '&') {
                                            break;
                                        }
                                    }
                                    var model = text_body.substring(index_model + 6, i);
                                    var index_res_id = text_body.indexOf("res_id=");
                                    for (i = index_res_id + 7; ; i++) {
                                        if (text_body[i] >= '0' && text_body[i] <= '9') {
                                            continue;
                                        } else {
                                            break;
                                        }
                                    }
                                    var res_id = text_body.substring(index_res_id + 7, i);
                                    self.do_action({
                                        type: 'ir.actions.act_window',
                                        res_model: model,
                                        res_id: parseInt(res_id),
                                        views: [[false, 'form']],
                                        target: 'current'
                                    })
                                };
                                self.do_notify(
                                    _t("Need Action From: ") + notif[1]['author_id'][1], tmp_text);
                            }
                        }
                    } catch (e) {
                        console.log(e)
                    }
                    self._handleNeedactionNotification(notif[1]);
                } else if (model === 'mail.channel') {
                    // new message in a channel
                    self._handleChannelNotification({
                        channelID: notif[0][2],
                        data: notif[1],
                    });
                } else if (model === 'res.partner') {
                    self._handlePartnerNotification(notif[1]);
                } else if (model === 'bus.presence') {
                    self._handlePresenceNotification(notif[1]);
                }
            });
        },
    });
    return MailManager;
});

odoo.define('advanced.mail.Chatter', function (require) {
    "use strict";
    var Chatter = require('mail.Chatter');
    Chatter.include({
        _updateMentionSuggestions: function () {
            if (!this.fields.followers) {
                return;
            }
            var self = this;

            this._mentionSuggestions = [];

            // add the followers to the mention suggestions
            var followerSuggestions = [];
            var followers = this.fields.followers.getFollowers();
            _.each(followers, function (follower) {
                if (follower.res_model === 'res.partner') {
                    followerSuggestions.push({
                        id: follower.res_id,
                        name: follower.name,
                        email: follower.email,
                    });
                }
            });
            if (followerSuggestions.length) {
                this._mentionSuggestions.push(followerSuggestions);
            }

            // add the partners (followers filtered out) to the mention suggestions
            // _.each(this._mentionPartnerSuggestions, function (partners) {
            //     self._mentionSuggestions.push(_.filter(partners, function (partner) {
            //         return !_.findWhere(followerSuggestions, { id: partner.id });
            //     }));
            // });
        },
    });
    return Chatter;
});

odoo.define('advanced.mail.Composer', function (require) {
    "use strict";
    var Composer = require('mail.Composer');
    var mailUtils = require('mail.utils');
    Composer.include({
        _mentionFetchPartners: function (search) {
            var self = this;
            return $.when(this._mentionPrefetchedPartners).then(function (prefetchedPartners) {
                // filter prefetched partners with the given search string
                var suggestions = [];
                var limit = self.options.mentionFetchLimit;
                var searchRegexp = new RegExp(_.str.escapeRegExp(mailUtils.unaccent(search)), 'i');
                _.each(prefetchedPartners, function (partners) {
                    if (limit > 0) {
                        var filteredPartners = _.filter(partners, function (partner) {
                            return partner.email && searchRegexp.test(partner.email) ||
                                partner.name && searchRegexp.test(mailUtils.unaccent(partner.name));
                        });
                        if (filteredPartners.length) {
                            suggestions.push(filteredPartners.substring(0, limit));
                            limit -= filteredPartners.length;
                        }
                    }
                });
                // if (!suggestions.length && !self.options.mentionPartnersRestricted) {
                //     // no result found among prefetched partners, fetch other suggestions
                //     suggestions = self._mentionFetchThrottled(
                //         'res.partner',
                //         'get_mention_suggestions',
                //         {limit: limit, search: search}
                //     );
                // }
                return suggestions;
            });
        },
    });
    return Composer;
});

odoo.define('advanced.mail.model.Message', function (require) {
    "use strict";
    var Message = require('mail.model.Message');
    var mailUtils = require('mail.utils');
    Message.include({
        getPreview: function () {
            var id, title;
            if (this.isLinkedToDocumentThread()) {
                id = this.getDocumentModel() + '_' + this.getDocumentID();
                title = this.getDocumentName();
            } else {
                id = 'mailbox_inbox';
                title = this.hasSubject() ? this.getSubject() : this.getDisplayedAuthor();
            }
            var content = "";
            if (this.getSubject() != false) {
                content = this.getSubject();
            } else {
                if (this.getTrackingValues()) {
                    for (var i = 0; i < this.getTrackingValues().length; i++) {
                        content += this.getTrackingValues()[i]['changed_field'] + ': ' + this.getTrackingValues()[i]['old_value'] + '->' + this.getTrackingValues()[i]['new_value'] + ", ";
                    }
                }
            }
            if (content.length < 1) {
                content = mailUtils.parseAndTransform(this.getBody(), mailUtils.inline);
            }
            return {
                author: "",
                body: content,
                date: this.getDate(),
                documentModel: this.getDocumentModel(),
                documentID: this.getDocumentID(),
                id: id,
                imageSRC: this._getModuleIcon() || this.getAvatarSource(),
                messageID: this.getID(),
                status: this.status,
                title: title,
            };
        },
    });
    return Message;
});