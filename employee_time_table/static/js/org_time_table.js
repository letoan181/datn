odoo.define("employee_time_table.time_working_table", function (require) {
    "use strict";
    var core = require('web.core');
    var ajax = require('web.ajax');
    var AbstractAction = require('web.AbstractAction');
    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;
    var data_table;
    var xml_load = ajax.loadXML(
        '/employee_time_table/static/xml/time_table_employee.xml',
        QWeb);
    var EmployeeTimeTable = AbstractAction.extend({
        hasControlPanel: false,
        events: {
            'input .employee_search input': '_onSearchEmp',
        },
        init: function (parent, context) {
            this._super(parent, context);
            var self = this;
            if (context.tag == 'time_working_table') {
                this._rpc({
                    model: 'hr.employee',
                    method: 'get_relate_timetable',
                    kwargs: [],
                }).then(function (result) {
                    data_table = result;
                    self.render();
                });
            }
        },
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            return this._super();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            // xml_load.then(function () {
            //            var org_chart = QWeb.render('employee_time_table.time_working_template', data_table);
            //            $(".o_control_panel").addClass("o_hidden");
            //            $(org_chart).prependTo(self.$el);
            //
            //        });
            // return org_chart;
            var org_chart = QWeb.render('employee_time_table.time_working_template', {value: data_table.data});
            $(".o_control_panel").addClass("o_hidden");
            $(org_chart).prependTo(self.$el);
            // if (context.tag == 'employee_time_table.time_working_table'){
            if (org_chart) {
                this.$el.find('.icon-leave').popover(
                    {
                        'content': function (e) {
                            var self = this;
                            var leave_id = this.firstElementChild.value;
                            // check if morning or afternoon
                            var leave_data = [];
                            var current_time_interval = parseInt($(this).attr('data-time-interval'));
                            _.each(data_table.data[0], function (data) {
                                if (data.leave_this_week) {
                                    _.each(data.leave_this_week, function (field) {
                                        if (field[2] == leave_id) {
                                            for (var i = 0; i < field[3].length; i++) {
                                                var added = false;
                                                for (var j = 0; j < leave_data.length; j++) {
                                                    if (field[3][i]['reason'] == leave_data[j]['reason'] && field[3][i]['leave_from'] == leave_data[j]['leave_from'] && field[3][i]['leave_to'] == leave_data[j]['leave_to']) {
                                                        added = true;
                                                    }
                                                }
                                                if (!added) {
                                                    if (current_time_interval == 0) {
                                                        if (parseInt(field[3][i]['leave_from'].substring(11, 13)) < 12) {
                                                            leave_data.push(field[3][i])
                                                        }
                                                    } else {
                                                        if (parseInt(field[3][i]['leave_to'].substring(11, 13)) >= 12) {
                                                            leave_data.push(field[3][i])
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    });
                                }
                            });
                            leave_data.sort(function (a, b) {
                                return a['leave_from'].localeCompare(b['leave_from'])
                            });
                            return QWeb.render('employee_time_table.leave', {value: leave_data})
                        },
                        'html': true,
                        'placement': function (c, s) {
                            return $(s).position().left < 200 ? 'left' : 'right'
                        },
                        'trigger': 'hover',
                    });
                this.$el.find('.icon-meeting').popover(
                    {
                        'content': function (e) {
                            var self = this;
                            var meeting_id = this.firstElementChild.value;
                            var meeting_data = [];
                            var meeting_data_af = [];
                            var check_id = [];
                            var current_time_interval = parseInt($(this).attr('data-time-interval'));
                            _.each(data_table.data[0], function (datax) {
                                if (datax.meeting_today) {
                                    _.each(datax.meeting_today, function (fieldx) {
                                        if (fieldx[2] == meeting_id) {
                                            _.each(fieldx[3], function (list) {
                                                // if (list[0] == true)
// if (list[0] == false)
                                                //     meeting_data_af.push([list[2][0], list[2][1], list[2][2]]);
                                                //check if exist
                                                var added = false;
                                                for (var i = 0; i < meeting_data.length; i++) {
                                                    if (list[3][0] == meeting_data[i][0] && list[3][1] == meeting_data[i][1] && list[3][2] == meeting_data[i][2]) {
                                                        added = true;
                                                    }
                                                }
                                                if (!added) {
                                                    if (current_time_interval == 0) {
                                                        if (list[3][1].substring(11, 13) < 12) {
                                                            meeting_data.push([list[3][0], list[3][1], list[3][2]]);
                                                        }
                                                    } else {
                                                        if (list[3][2].substring(11, 13) >= 12) {
                                                            meeting_data.push([list[3][0], list[3][1], list[3][2]]);
                                                        }
                                                    }
                                                }
                                            })
                                        }
                                    });
                                }
                            });
// // if (meeting_data_mo)
                            // //     return QWeb.render('employee_time_table.meeting', {value: meeting_data_mo});
                            meeting_data.sort(function (a, b) {
                                return a[1].localeCompare(b[1])
                            });
                            return QWeb.render('employee_time_table.meeting', {value: meeting_data});
                        },
                        'html': true,
                        'placement': function (c, s) {
                            return $(s).position().left < 200 ? 'left' : 'right'
                        },
                        'trigger': 'hover',
                    });
                // // hover cho timesheet
                this.$el.find('.timesheet').popover(
                    {
                        'content': function (e) {
                            var self = this;
                            var employee_id = this.firstElementChild.value;
                            var timesheet_data = [];
                            _.each(data_table.data[0], function (datai) {
                                if (datai.timesheet) {
                                    _.each(datai.timesheet, function (fieldi) {
                                        if (fieldi[0] == employee_id) {
                                            var total_timesheet_tmp = fieldi[1].total_timesheet;
                                            var week_timesheet_tmp = fieldi[1].week_timesheet;
                                            var today_timesheet_tmp = fieldi[1].today_timesheet;
                                            if (total_timesheet_tmp) {
                                                total_timesheet_tmp = Math.round(total_timesheet_tmp * 100) / 100
                                            }
                                            if (week_timesheet_tmp) {
                                                week_timesheet_tmp = Math.round(week_timesheet_tmp * 100) / 100
                                            }
                                            if (today_timesheet_tmp) {
                                                today_timesheet_tmp = Math.round(today_timesheet_tmp * 100) / 100
                                            }
                                            timesheet_data.push(total_timesheet_tmp, week_timesheet_tmp, today_timesheet_tmp)
                                        }
                                    })
                                }
                            });
                            var timesheet_detail = QWeb.render('employee_time_table.timesheet', {value: timesheet_data});
                            return timesheet_detail
                        },
                        'html': true,
                        'placement': function (c, s) {
                            return $(s).position().left < 200 ? 'right' : 'left'
                        },
                        'trigger': 'hover',
                    });
// hover cho dayoff vao thu 2
                this.$el.find('.flag-mon').popover(
                    {
                        'content': function (e) {
                            var dayoff_data = [];
                            _.each(data_table.data[4], function (datax) {
                                if (datax[0] == 0) {
                                    dayoff_data.push(datax[2])
                                }
                            });
                            return QWeb.render('attendance.day.off.description', {value: dayoff_data});
                        },
                        'html': true,
                        'placement': function (c, s) {
                            return $(s).position().left < 200 ? 'bottom' : 'top'
                        },
                        'trigger': 'hover',
                    });
                // hover cho dayoff vao thu 3
                this.$el.find('.flag-tue').popover(
                    {
                        'content': function (e) {
                            var dayoff_data = [];
                            _.each(data_table.data[4], function (datax) {
                                if (datax[0] == 1) {
                                    dayoff_data.push(datax[2])
                                }
                            });
                            return QWeb.render('attendance.day.off.description', {value: dayoff_data});
                        },
                        'html': true,
                        'placement': function (c, s) {
                            return $(s).position().left < 200 ? 'bottom' : 'top'
                        },
                        'trigger': 'hover',
                    });
                // hover cho dayoff vao thu 4
                this.$el.find('.flag-wed').popover(
                    {
                        'content': function (e) {
                            var dayoff_data = [];
                            _.each(data_table.data[4], function (datax) {
                                if (datax[0] == 2) {
                                    dayoff_data.push(datax[2])
                                }
                            });
                            return QWeb.render('attendance.day.off.description', {value: dayoff_data});
                        },
                        'html': true,
                        'placement': function (c, s) {
                            return $(s).position().left < 200 ? 'bottom' : 'top'
                        },
                        'trigger': 'hover',
                    });
                // hover cho dayoff vao thu 5
                this.$el.find('.flag-thu').popover(
                    {
                        'content': function (e) {
                            var dayoff_data = [];
                            _.each(data_table.data[4], function (datax) {
                                if (datax[0] == 3) {
                                    dayoff_data.push(datax[2])
                                }
                            });
                            return QWeb.render('attendance.day.off.description', {value: dayoff_data});
                        },
                        'html': true,
                        'placement': function (c, s) {
                            return $(s).position().left < 200 ? 'bottom' : 'top'
                        },
                        'trigger': 'hover',
                    });
                // hover cho dayoff vao thu 6
                this.$el.find('.flag-fri').popover(
                    {
                        'content': function (e) {
                            var dayoff_data = [];
                            _.each(data_table.data[4], function (datax) {
                                if (datax[0] == 4) {
                                    dayoff_data.push(datax[2])
                                }
                            });
                            return QWeb.render('attendance.day.off.description', {value: dayoff_data});
                        },
                        'html': true,
                        'placement': function (c, s) {
                            return $(s).position().left < 200 ? 'bottom' : 'top'
                        },
                        'trigger': 'hover',
                    });
                // hover cho dayoff vao thu 7
                this.$el.find('.flag-sat').popover(
                    {
                        'content': function (e) {
                            var dayoff_data = [];
                            _.each(data_table.data[4], function (datax) {
                                if (datax[0] == 5) {
                                    dayoff_data.push(datax[2])
                                }
                            });
                            return QWeb.render('attendance.day.off.description', {value: dayoff_data});
                        },
                        'html': true,
                        'placement': function (c, s) {
                            return $(s).position().left > 200 ? 'top' : 'bottom'
                        },
                        'trigger': 'hover',
                    });
// update filter feature
                self._filter_sub_coordinator();
                self._filter_same_level();
                self._filter_boss();
                return org_chart;
            }
        },
        reload: function () {
            window.location.href = this.href;
        },
        _onSearchEmp: function (event) {
            var self = this;
            var search = $(event.currentTarget).val().toLowerCase().trim();
            search = self.fix_vietnam(search);
            var all = this.$el.find('.employee-line');
            _.each(all, function (element) {
                // moi element log ra data-name
                var current_element_name = $(element).attr('data-name').toLowerCase().trim();
                current_element_name = self.fix_vietnam(current_element_name);
                if (current_element_name.includes(search)) {
                    $(element).show();
                } else {
                    $(element).hide();
                }
// emp.invisible = search ? emp.id.indexOf(search) < 0 : false;
            });
        }
        //this._updateDropdownFields();
        ,
        _filter_sub_coordinator: function (event) {
            var all = this.$el.find('.employee-line');
            $('#sub_coordinator').click(function (e) {
                if ($('#sub_coordinator:checkbox:checked').length > 0) {
                    $("#same_level").prop("checked", false);
                }
                if ($('#bossie:checkbox:checked').length > 0) {
                    $("#bossie").prop("checked", false);
                }
                if ($('#sub_coordinator:checkbox:checked').length > 0) {
                    var sub_coordinator_list = [];
                    if (data_table.data[5]) {
                        sub_coordinator_list = data_table.data[5].sub_coordinator;
                    }
                    _.each(all, function (element) {
                        var current_element_name = $(element).attr('data-name');
                        if (sub_coordinator_list.includes(current_element_name)) {
                            $(element).show();
                        } else {
                            $(element).hide();
                        }
                    });
                } else {
                    _.each(all, function (element) {
                        $(element).show();
                    });
                }
            })
        }
        ,
        _filter_same_level: function (event) {
            var all = this.$el.find('.employee-line');
            $('#same_level').click(function (e) {
                if ($('#same_level:checkbox:checked').length > 0) {
                    $("#sub_coordinator").prop("checked", false);
                }
                if ($('#same_level:checkbox:checked').length > 0) {
                    $("#bossie").prop("checked", false);
                }
                if ($('#same_level:checkbox:checked').length > 0) {
                    var same_level_list = [];
                    if (data_table.data[5]) {
                        same_level_list = data_table.data[5].same_level;
                    }
                    _.each(all, function (element) {
                        var current_element_name = $(element).attr('data-name');
                        if (same_level_list.includes(current_element_name)) {
                            $(element).show();
                        } else {
                            $(element).hide();
                        }
                    });
                } else {
                    _.each(all, function (element) {
                        $(element).show();
                    });
                }
            })
        }
        ,
        _filter_boss: function (event) {
            var all = this.$el.find('.employee-line');
            $('#bossie').click(function (e) {
                if ($('#bossie:checkbox:checked').length > 0) {
                    $("#sub_coordinator").prop("checked", false);
                }
                if ($('#bossie:checkbox:checked').length > 0) {
                    $("#same_level").prop("checked", false);
                }
                if ($('#bossie:checkbox:checked').length > 0) {
                    var bossie_list = [];
                    if (data_table.data[5]) {
                        bossie_list = data_table.data[5].manager;
                    }
                    _.each(all, function (element) {
                        var current_element_name = $(element).attr('data-name');
                        if (bossie_list.includes(current_element_name)) {
                            $(element).show();
                        } else {
                            $(element).hide();
                        }
                    });
                } else {
                    _.each(all, function (element) {
                        $(element).show();
                    });
                }
            })
        }
        ,
        fix_vietnam: function (str) {
            str = str.replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g, "a");
            str = str.replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g, "e");
            str = str.replace(/ì|í|ị|ỉ|ĩ/g, "i");
            str = str.replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g, "o");
            str = str.replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g, "u");
            str = str.replace(/ỳ|ý|ỵ|ỷ|ỹ/g, "y");
            str = str.replace(/đ/g, "d");
            str = str.replace(/À|Á|Ạ|Ả|Ã|Â|Ầ|Ấ|Ậ|Ẩ|Ẫ|Ă|Ằ|Ắ|Ặ|Ẳ|Ẵ/g, "A");
            str = str.replace(/È|É|Ẹ|Ẻ|Ẽ|Ê|Ề|Ế|Ệ|Ể|Ễ/g, "E");
            str = str.replace(/Ì|Í|Ị|Ỉ|Ĩ/g, "I");
            str = str.replace(/Ò|Ó|Ọ|Ỏ|Õ|Ô|Ồ|Ố|Ộ|Ổ|Ỗ|Ơ|Ờ|Ớ|Ợ|Ở|Ỡ/g, "O");
            str = str.replace(/Ù|Ú|Ụ|Ủ|Ũ|Ư|Ừ|Ứ|Ự|Ử|Ữ/g, "U");
            str = str.replace(/Ỳ|Ý|Ỵ|Ỷ|Ỹ/g, "Y");
            str = str.replace(/Đ/g, "D");
            return str;
        }
    });
    core.action_registry.add('time_working_table', EmployeeTimeTable);
    return {
        EmployeeTimeTable: EmployeeTimeTable
    };
});
