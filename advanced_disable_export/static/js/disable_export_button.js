odoo.define("web_disable_export_button", function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var ListController = require('web.ListController');
    var FormController = require('web.FormController');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var WebClient = require('web.WebClient');
    var session = require('web.session');
    var _t = core._t;
    var Sidebar = require('web.Sidebar');
    KanbanController.include({
        renderButtons: function ($node) {
            var self = this;
            this._super.apply(this, arguments);
            if (this.$buttons) {
                if (self.modelName.includes('document')) {
                    this.$buttons.find('.o_button_import').hide();
                } else if (self.modelName == 'crm.lead') {
                    // var has_export_group = false;
                    var has_import_group = false;
                    this.getSession().user_has_group('advanced_disable_export.group_import_lead').then(function (has_group_i) {
                        if (has_group_i == true) {
                            has_import_group = true;
                        } else {
                            has_import_group = false;
                        }
                        if (has_import_group == false) {
                            self.$buttons.find('.o_button_import').hide();
                        }
                    });

                } else {
                    this._rpc({
                        model: 'advanced.disable.action',
                        method: 'get_action_permission',
                        kwargs: {
                            user_id: session.uid,
                            model: self.modelName,
                            type: 'import',
                        }
                    }).then(function (result) {
                        if (result == false) {
                            self.$buttons.find('.o_button_import').hide();
                        }
                    });

                }
            }
        },
    });
    ListController.include({
        renderButtons: function ($node) {
            var self = this;
            this._super.apply(this, arguments);
            if (this.$buttons) {
                if (self.modelName.includes('document')) {
                    self.$buttons.find('.o_button_import').remove();
                    self.$buttons.find('.o_list_export_xlsx').remove();
                } else if (self.modelName == 'crm.lead') {
                    self.$buttons.find('.o_list_export_xlsx').remove();
                    var has_import_group = false;
                    this.getSession().user_has_group('advanced_disable_export.group_import_lead').then(function (has_group_i) {
                        if (has_group_i == true) {
                            has_import_group = true;
                        } else {
                            has_import_group = false;
                        }
                        if (has_import_group == false) {
                            self.$buttons.find('.o_button_import').remove();
                        }
                    });
                } else {
                    this._rpc({
                        model: 'advanced.disable.action',
                        method: 'get_action_permission',
                        kwargs: {
                            user_id: session.uid,
                            model: self.modelName,
                            type: 'import'
                        }
                    }).then(function (result) {
                        if (result == false) {
                            self.$buttons.find('.o_button_import').hide();
                        }
                    });
                    this._rpc({
                        model: 'advanced.disable.action',
                        method: 'get_action_permission',
                        kwargs: {
                            user_id: session.uid,
                            model: self.modelName,
                            type: 'export_all'
                        }
                    }).then(function (result) {
                        if (result == false) {
                            self.$buttons.find('.o_list_export_xlsx').hide();
                        }
                    });
                }
            }

        },
        renderSidebar: function ($node) {
            var model = this.modelName;
            var self = this;
            if (this.hasSidebar && model.includes('document')) {
                var other = [];
                if (this) {
                    other.push({
                        label: _t("Delete"),
                        callback: this._onDeleteSelectedRecords.bind(this)
                    });
                }
                this.sidebar = new Sidebar(this, {
                    editable: this.is_action_enabled('edit'),
                    env: {
                        context: this.model.get(this.handle, {raw: true}).getContext(),
                        activeIds: this.getSelectedIds(),
                        model: this.modelName,
                    },
                    actions: _.extend(this.toolbarActions, {other: other}),
                });
                return this.sidebar.appendTo($node).then(function () {
                    self._toggleSidebar();
                });
            } else {
                this._super.apply(this, arguments);
            }
        },
        _onExportData: function () {
            var self = this;
            if (this.modelName == 'crm.lead') {
                this.getSession().user_has_group('advanced_disable_export.group_export_lead').then(function (has_group) {
                    if (has_group == true) {
                        this._getExportDialogWidget().open();
                    } else {
                        Dialog.alert(this, "You Don't Have Permission To Export Leads");
                    }
                }.bind(this));
            } else {
                this._rpc({
                    model: 'advanced.disable.action',
                    method: 'get_action_permission',
                    kwargs: {
                        user_id: session.uid,
                        model: self.modelName,
                        type: 'export'
                    }
                }).then(function (result) {
                    if (result == false) {
                        Dialog.alert(this, "You Don't Have Permission To Export");
                    } else {
                        this._getExportDialogWidget().open();
                    }
                }.bind(this));
            }
        },
        _toggleArchiveState: function (archive) {
            var self = this;
            this._rpc({
                model: 'advanced.disable.action',
                method: 'get_action_permission',
                kwargs: {
                    user_id: session.uid,
                    model: self.modelName,
                    type: 'archive'
                }
            }).then(function (result) {
                if (result == false) {
                    Dialog.alert(this, "Archive Disable On Model");
                } else {
                    this._archive(this.selectedRecords, archive);
                }
            }.bind(this));

        },
    });
    FormController.include({
        _toggleArchiveState: function (archive) {
            var self = this;
            this._rpc({
                model: 'advanced.disable.action',
                method: 'get_action_permission',
                kwargs: {
                    user_id: session.uid,
                    model: self.modelName,
                    type: 'archive'
                }
            }).then(function (result) {
                if (result == false) {
                    Dialog.alert(this, "Archive Disable On Model");
                } else {
                    this._archive([this.handle], archive);
                }
            }.bind(this));

        },
    });
});
