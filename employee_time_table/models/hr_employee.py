# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta, date, datetime

import pytz
from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import models, api, fields
from odoo.fields import Datetime
from odoo.http import request


class EmployeeTimeTable(models.Model):
    _inherit = 'hr.employee'

    employee_can_see_leave = []
    month_of_birth = fields.Integer(string="Month Of Birth", compute='_compute_month_of_birth', store=True)
    date_month_of_birth = fields.Char(string="Date Month Of Birth", compute='_compute_date_month_of_birth', store=True)

    @api.depends('birthday')
    def _compute_month_of_birth(self):
        for employee in self:
            if employee.birthday:
                employee.month_of_birth = employee.birthday.month
            else:
                employee.month_of_birth = 0

    @api.depends('birthday')
    def _compute_date_month_of_birth(self):
        for employee in self:
            if employee.birthday:
                month_str = str(employee.birthday.month)
                if len(month_str) == 1:
                    month_str = '0' + month_str
                day_str = str(employee.birthday.day)
                if len(day_str) == 1:
                    day_str = '0' + day_str
                employee.date_month_of_birth = month_str + '/' + day_str
            else:
                employee.date_month_of_birth = ''

    @api.model
    def get_relate_timetable(self):
        if self._uid:
            employees = []
            employee_ids = []
            filter_employees = {}
            filter_manager = []
            filter_same_level = []
            filter_sub_coordinator = []
            employee = self.env['hr.employee'].sudo().search(
                [('user_id', '=', self._uid), ('active', '=', True)], limit=1)
            employee_department_id = employee.department_id.id
            department_name = employee.department_id.name
            # neu la admin, xem toan bo nhan vien
            if self.user_has_groups('employee_time_table.group_admin_timetable'):
                employees = self.env['hr.employee'].sudo().search([])
                sub_coordinator = self.env['hr.employee'].sudo().search([('parent_id', '=', employee.id)])
                if len(sub_coordinator) > 0:
                    for e in sub_coordinator:
                        filter_sub_coordinator.append(e.name)
            # neu khong, chi xem nhan vien trong phong minh va sep
            else:
                # find all employees in 1 department
                if employee.parent_id:
                    emps = self.env['hr.employee'].sudo().search([('department_id', '=', employee_department_id)])
                    # push in to array employees
                    for e in emps:
                        if e not in employees:
                            employees.append(e)
                            employee_ids.append(e.id)
                else:
                    employees.append(employee)
                    employee_ids.append(employee.id)
                # find all managers
                if employee.parent_id:
                    manager = self.get_all_manager(employee.parent_id)
                    if manager:
                        for e in manager:
                            filter_manager.append(e.name)
                            if e.id not in employee_ids:
                                employees += e
                # find all sub manager
                sub_coordinator = self.env['hr.employee'].sudo().search([('parent_id', '=', employee.id)])
                if len(sub_coordinator) > 0:
                    for e in sub_coordinator:
                        filter_sub_coordinator.append(e.name)
                        if e.id not in self.employee_can_see_leave:
                            self.employee_can_see_leave.append(e.id)
                        if e.id not in employee_ids:
                            employees += e
                # find same level manager
                if employee.parent_id:
                    same_level = self.env['hr.employee'].sudo().search([('parent_id', '=', employee.parent_id.id)])
                    if len(same_level) > 0:
                        for e in same_level:
                            filter_same_level.append(e.name)
                            if e.id not in employee_ids:
                                employees += e

            # filter boss, sub_coordinators and same_level managers
            filter_employees.update({
                'manager': filter_manager,
                'sub_coordinator': filter_sub_coordinator,
                'same_level': filter_same_level
            })

            # find working days, leaves and meetings of one employee
            time_table_data = []
            today = self.get_today()
            get_date = self.get_date()
            dayoff = self.get_dayoff()
            # get data functions
            index = 0
            for employee in employees:
                time_working = self.get_time_working(employee)
                working_duration = self.get_working_duration(employee)
                timesheet = self.get_timesheet(employee)
                leave, index = self.get_leave_this_week(employee, index)
                index += 1
                meeting, index = self.get_meeting_this_week(employee, index)
                index += 1
                image = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url') + '/web/image?model=hr.employee&id=' + str(employee.id) + '&field=image_128',
                time_table_data.append({
                    'id': employee.id,
                    'employee': employee.name,
                    'working_duration': working_duration,
                    'work_time': time_working,
                    'timesheet': timesheet,
                    'leave_this_week': leave,
                    'meeting_today': meeting,
                    'image': image
                })
            value = {
                'data': [time_table_data, today, department_name, get_date, dayoff, filter_employees]
            }
            return value

    # get department manager and his managers
    def get_all_manager(self, emp):
        result = [emp]  # result = current array
        if emp.parent_id:  # if employee has manager
            current_parent = self.get_all_manager(emp.parent_id)  # recursive: emp = emp + parent
            if current_parent and len(current_parent) > 0:  # parent != null
                for e in current_parent:
                    result.append(e)  # add manager into list of employees
        return result

    def get_timezone(self):
        # get timezone
        user_time_zone = pytz.UTC
        if self.env.user.partner_id.tz:
            # change the timezone to the timezone of the user
            user_time_zone = pytz.timezone(self.env.user.partner_id.tz)
        return user_time_zone.zone

    def get_today(self):
        # return today
        today = Datetime.now().weekday()
        return today

    def get_date(self):
        start = date.today() - timedelta(days=date.today().weekday())
        date_found = {}
        date_found.update({
            'Monday': (start + timedelta(days=0)).strftime("%d/%m/%Y"),
            'Tuesday': (start + timedelta(days=1)).strftime("%d/%m/%Y"),
            'Wednesday': (start + timedelta(days=2)).strftime("%d/%m/%Y"),
            'Thursday': (start + timedelta(days=3)).strftime("%d/%m/%Y"),
            'Friday': (start + timedelta(days=4)).strftime("%d/%m/%Y"),
            'Saturday': (start + timedelta(days=5)).strftime("%d/%m/%Y"),
        })
        return date_found

    # check if having leaves this week,
    # find from start to end (a week) to find if having any leave in that time,
    # if yes, for each leave, check when it happends
    # then if an employee has leaves, update meeting data in his timetable
    def get_leave_this_week(self, employee, index):
        # get all leaves of one employee, if have one, put into leave_this_week
        # leave's format:{morning,afternoon, data}
        # get now
        this_week = Datetime.now()
        # start time = daytime now - day = time
        start = this_week - timedelta(days=this_week.weekday())
        # end = start time + next week(6 days later)
        end = start + timedelta(days=6)
        # get all leaves of employee in this week that are approved
        leaves = request.env['hr.leave'].sudo().search(
            [('date_to', '>=', str(start)), ('date_from', '<=', str(end)), ('employee_id', '=', employee.id),
             ('state', '=', 'validate')])
        check_leave = []
        leave_this_week = {}

        # if having leaves, consider due to cases when it happens
        if len(leaves) > 0:
            for leave in leaves:
                index += 1
                # if start <= leave.date_from <= end and leave.holiday_id.employee_id == employee:
                if self.user_has_groups(
                        'employee_time_table.group_admin_timetable') or self._uid == employee.user_id.id:
                    leave_reason = leave.name
                elif employee.id in self.employee_can_see_leave:
                    leave_reason = leave.name
                else:
                    leave_reason = '***** ***** *****'

                leave_from = leave.date_from.astimezone(timezone(self.get_timezone()))
                leave_to = leave.date_to.astimezone(timezone(self.get_timezone()))
                leave_start_standard_visual = leave_from.strftime("%d/%m/%Y %H:%M")
                leave_stop_standard_visual = leave_to.strftime("%d/%m/%Y %H:%M")
                # case: leave unit hours
                if leave.request_unit_hours:
                    check_leave.append(leave.date_from.astimezone(timezone(self.get_timezone())).weekday())
                    day = leave_from.strftime("%A")
                    # need handle
                    if int(leave_from.strftime("%H")) < 13 and int(leave_to.strftime("%H")) < 13:
                        if not leave_this_week.get(day):
                            leave_this_week.update({
                                day: [True, False, index, [{
                                    'reason': leave_reason,
                                    'leave_from': leave_start_standard_visual,
                                    'leave_to': leave_stop_standard_visual,
                                }]]
                            })
                        else:
                            leave_this_week.get(day)[0] = True
                            leave_this_week.get(day)[3].append({
                                'reason': leave_reason,
                                'leave_from': leave_start_standard_visual,
                                'leave_to': leave_stop_standard_visual,
                            })
                    elif int(leave_from.strftime("%H")) >= 13 and int(leave_to.strftime("%H")) >= 13:
                        if not leave_this_week.get(day):
                            leave_this_week.update({
                                day: [False, True, index, [{
                                    'reason': leave_reason,
                                    'leave_from': leave_start_standard_visual,
                                    'leave_to': leave_stop_standard_visual,
                                }]]
                            })
                        else:
                            leave_this_week.get(day)[1] = True
                            leave_this_week.get(day)[3].append({
                                'reason': leave_reason,
                                'leave_from': leave_start_standard_visual,
                                'leave_to': leave_stop_standard_visual,
                            })
                    else:
                        if not leave_this_week.get(day):
                            leave_this_week.update({
                                day: [True, True, index, [{
                                    'reason': leave_reason,
                                    'leave_from': leave_start_standard_visual,
                                    'leave_to': leave_stop_standard_visual,
                                }]]
                            })
                        else:
                            leave_this_week.get(day)[0] = True
                            leave_this_week.get(day)[1] = True
                            leave_this_week.get(day)[3].append({
                                'reason': leave_reason,
                                'leave_from': leave_start_standard_visual,
                                'leave_to': leave_stop_standard_visual,
                            })
                # case: leave half a day
                elif leave.request_unit_half:
                    check_leave.append(leave.date_from.astimezone(timezone(self.get_timezone())).weekday())
                    day = leave.date_from.astimezone(timezone(self.get_timezone())).strftime("%A")
                    # leave in the morning
                    if leave.request_date_from_period == 'am':
                        if not leave_this_week.get(day):
                            leave_this_week.update({
                                day: [True, False, index, [{
                                    'reason': leave_reason,
                                    'leave_from': leave_start_standard_visual,
                                    'leave_to': leave_stop_standard_visual,
                                }]]
                            })
                        else:
                            leave_this_week.get(day)[0] = True
                            leave_this_week.get(day)[3].append({
                                'reason': leave_reason,
                                'leave_from': leave_start_standard_visual,
                                'leave_to': leave_stop_standard_visual,
                            })
                    # leave in the afternoon
                    if leave.request_date_from_period == 'pm':
                        if not leave_this_week.get(day):
                            leave_this_week.update({
                                day: [False, True, index, [{
                                    'reason': leave_reason,
                                    'leave_from': leave_start_standard_visual,
                                    'leave_to': leave_stop_standard_visual,
                                }]]
                            })
                        else:
                            leave_this_week.get(day)[1] = True
                            leave_this_week.get(day)[3].append({
                                'reason': leave_reason,
                                'leave_from': leave_start_standard_visual,
                                'leave_to': leave_stop_standard_visual,
                            })
                # other cases
                else:
                    # case leave day=1
                    if leave.number_of_days == 1:
                        check_leave.append(leave.date_from.astimezone(timezone(self.get_timezone())).weekday())
                        day = leave.date_from.astimezone(timezone(self.get_timezone())).strftime("%A")
                        if not leave_this_week.get(day):
                            leave_this_week.update({
                                day: [True, True, index, [{
                                    'reason': leave_reason,
                                    'leave_from': leave_start_standard_visual,
                                    'leave_to': leave_stop_standard_visual,
                                }]]
                            })
                        else:
                            leave_this_week.get(day)[0] = True
                            leave_this_week.get(day)[1] = True
                            leave_this_week.get(day)[3].append({
                                'reason': leave_reason,
                                'leave_from': leave_start_standard_visual,
                                'leave_to': leave_stop_standard_visual,
                            })
                    # case leave day > 1
                    else:
                        num_of_days = (int)(leave.number_of_days)
                        for single_date in [d for d in
                                            (leave.date_from.astimezone(timezone(self.get_timezone())) + timedelta(n)
                                             for n in
                                             range(num_of_days)) if
                                            d <= leave.date_to.astimezone(timezone(self.get_timezone()))]:
                            day = single_date.strftime("%A")
                            check_leave.append(single_date.weekday())
                            if not leave_this_week.get(day):
                                leave_this_week.update({
                                    day: [True, True, index, [{
                                        'reason': leave_reason,
                                        'leave_from': leave_start_standard_visual,
                                        'leave_to': leave_stop_standard_visual,
                                    }]]
                                })
                                index += 1
                            else:
                                leave_this_week.get(day)[0] = True
                                leave_this_week.get(day)[1] = True
                                leave_this_week.get(day)[3].append({
                                    'reason': leave_reason,
                                    'leave_from': leave_start_standard_visual,
                                    'leave_to': leave_stop_standard_visual,
                                })
        # no leaves, return false
        day_off = 'None'
        for i in range(6):
            if i not in check_leave:
                if i == 0:
                    day_off = 'Monday'
                if i == 1:
                    day_off = 'Tuesday'
                if i == 2:
                    day_off = 'Wednesday'
                if i == 3:
                    day_off = 'Thursday'
                if i == 4:
                    day_off = 'Friday'
                if i == 5:
                    day_off = 'Saturday'
                leave_this_week.update({
                    day_off: [False, False, False, {
                        'reason': '',
                        'leave_from': '',
                        'leave_to': '',
                    }]
                })
        return leave_this_week, index

    # check each half day in a day in one week, if one attends, return true, else return false
    def get_time_working(self, employee):
        time_woking_data = {}
        weekday = 'None'
        check_day_exist = []
        if employee:
            working_hour = employee.resource_calendar_id.attendance_ids
            for attendance in working_hour:
                if attendance.day_period == 'morning':
                    if attendance.dayofweek == '0':
                        weekday = 'Monday'
                        check_day_exist.append(int(attendance.dayofweek))
                        time_woking_data.update({
                            weekday: [True, False],
                        })
                    if attendance.dayofweek == '1':
                        weekday = 'Tuesday'
                        check_day_exist.append(int(attendance.dayofweek))
                        time_woking_data.update({
                            weekday: [True, False],
                        })
                    if attendance.dayofweek == '2':
                        weekday = 'Wednesday'
                        check_day_exist.append(int(attendance.dayofweek))
                        time_woking_data.update({
                            weekday: [True, False],
                        })
                    if attendance.dayofweek == '3':
                        weekday = 'Thursday'
                        check_day_exist.append(int(attendance.dayofweek))
                        time_woking_data.update({
                            weekday: [True, False],
                        })
                    if attendance.dayofweek == '4':
                        weekday = 'Friday'
                        check_day_exist.append(int(attendance.dayofweek))
                        time_woking_data.update({
                            weekday: [True, False],
                        })
                    if attendance.dayofweek == '5':
                        weekday = 'Saturday'
                        check_day_exist.append(int(attendance.dayofweek))
                        time_woking_data.update({
                            weekday: [True, False],
                        })

                if attendance.day_period == 'afternoon':
                    if attendance.dayofweek == '0':
                        weekday = 'Monday'
                        if 0 in check_day_exist:
                            time_woking_data.update({
                                weekday: [True, True],
                            })
                        else:
                            check_day_exist.append(int(attendance.dayofweek))
                            time_woking_data.update({
                                weekday: [False, True],
                            })
                    if attendance.dayofweek == '1':
                        weekday = 'Tuesday'
                        if 1 in check_day_exist:
                            time_woking_data.update({
                                weekday: [True, True],
                            })
                        else:
                            check_day_exist.append(int(attendance.dayofweek))
                            time_woking_data.update({
                                weekday: [False, True],
                            })
                    if attendance.dayofweek == '2':
                        weekday = 'Wednesday'
                        if 2 in check_day_exist:
                            time_woking_data.update({
                                weekday: [True, True],
                            })
                        else:
                            check_day_exist.append(int(attendance.dayofweek))
                            time_woking_data.update({
                                weekday: [False, True],
                            })
                    if attendance.dayofweek == '3':
                        weekday = 'Thursday'
                        if 3 in check_day_exist:
                            time_woking_data.update({
                                weekday: [True, True],
                            })
                        else:
                            check_day_exist.append(int(attendance.dayofweek))
                            time_woking_data.update({
                                weekday: [False, True],
                            })
                    if attendance.dayofweek == '4':
                        weekday = 'Friday'
                        if 4 in check_day_exist:
                            time_woking_data.update({
                                weekday: [True, True],
                            })
                        else:
                            check_day_exist.append(int(attendance.dayofweek))
                            time_woking_data.update({
                                weekday: [False, True],
                            })
                    if attendance.dayofweek == '5':
                        weekday = 'Saturday'
                        if 5 in check_day_exist:
                            time_woking_data.update({
                                weekday: [True, True],
                            })
                        else:
                            check_day_exist.append(int(attendance.dayofweek))
                            time_woking_data.update({
                                weekday: [False, True],
                            })
            day_off = 'None'
            for i in range(6):
                if i not in check_day_exist:
                    if i == 0:
                        day_off = 'Monday'
                    if i == 1:
                        day_off = 'Tuesday'
                    if i == 2:
                        day_off = 'Wednesday'
                    if i == 3:
                        day_off = 'Thursday'
                    if i == 4:
                        day_off = 'Friday'
                    if i == 5:
                        day_off = 'Saturday'
                    time_woking_data.update({
                        day_off: [False, False]
                    })

        return time_woking_data

    # get employee's working duration
    def get_working_duration(self, employee):
        working_duration_data = {}
        today = Datetime.now()
        if employee:
            working_duration = relativedelta(today, employee.create_date)
            day = working_duration.days
            month = working_duration.months
            year = working_duration.years
            working_duration_data.update({
                'day': day,
                'month': month,
                'year': year
            })
        return working_duration_data

    def get_timesheet(self, employee):
        timesheet_duration = []
        timesheet_id = employee.id
        today = date.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        # lay tat ca time sheet cua employee
        self.env.cr.execute(
            """SELECT SUM(unit_amount) FROM account_analytic_line WHERE employee_id = %s""",
            (employee.id,))
        get_total_timesheet = self.env.cr.fetchall()

        self._cr.execute(
            'SELECT SUM(unit_amount) FROM account_analytic_line WHERE employee_id = %s AND %s <= date AND date <= %s',
            (employee.id, start, end))
        get_this_week_timesheet = self.env.cr.fetchall()

        self._cr.execute('SELECT SUM(unit_amount) FROM account_analytic_line WHERE employee_id = %s AND date = %s',
                         (employee.id, today))
        get_today_timesheet = self.env.cr.fetchall()
        timesheet_duration.append(
            [timesheet_id, {
                'total_timesheet': get_total_timesheet,
                'week_timesheet': get_this_week_timesheet,
                'today_timesheet': get_today_timesheet
            }]
        )

        return timesheet_duration

    # def set_dayoff(self):
    def get_dayoff(self):
        today = date.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        set_dayoff = request.env['attendance.day.off'].sudo().search(
            [('set_day', '>=', str(start)), ('set_day', '<=', str(end))])
        get_day = self.get_date()
        list_day = []
        check_day = []
        for rec in get_day:
            list_day.append(get_day[rec])
        is_dayoff = {}
        for e in set_dayoff:
            if e.set_day.strftime("%d/%m/%Y") in list_day:
                check_day.append(e.set_day.weekday())
                is_dayoff.update({
                    e.get_weekday: [e.set_day.weekday(), True, e.description]
                })
        day_off = 'None'
        for i in range(6):
            if i not in check_day:
                if i == 0:
                    day_off = 'Monday'
                if i == 1:
                    day_off = 'Tuesday'
                if i == 2:
                    day_off = 'Wednesday'
                if i == 3:
                    day_off = 'Thursday'
                if i == 4:
                    day_off = 'Friday'
                if i == 5:
                    day_off = 'Saturday'
                is_dayoff.update({
                    day_off: [i, False, 'Let\'s work hard!']
                })
        return is_dayoff

    # check if having meetings this week,
    # find from start to end (a week) to find if having any meeting in that time,
    # if yes, for each meeting, find all attendees,
    # then if an employee in the company attends the meeting, update meeting data in his timetable
    def get_meeting_this_week(self, employee, index):  # meeting_today = [id(int), [name, start, stop]]
        # tim tat ca cac leave cua nhan vien trong tuan nay
        # tim tat ca cac event duoc tao ra sau khi approve
        # tim tat ca cac meeting trong tuan nay khong nam trong nhung meeting trong buoc tren
        # , ('id', 'not in', leave_ids)
        leaves = request.env['hr.leave'].sudo().search([('state', '=', 'validate')])
        leave_ids = []
        for e in leaves:
            leave_ids.append(e.meeting_id.id)
        today = Datetime.now()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        meetings = request.env['calendar.event'].sudo().search(
            [('stop', '>=', str(start)), ('start', '<=', str(end)), ('id', 'not in', leave_ids)])
        meeting_this_week_ids = []
        for e in meetings.ids:
            if isinstance(e, int):
                meeting_this_week_ids.append(e)
        # tim tat ca cac meeting employee nay tham gia trong khoang thoi gian tuan nay
        calendar_attendee_this_week = request.env['calendar.attendee'].sudo().search(
            [('event_id', 'in', meeting_this_week_ids), ('partner_id', '=', employee.user_id.partner_id.id),
             ('state', '=', 'accepted')])
        # set quyen truy cap tat ca meeting cho admin
        # admin = request.env['res.groups'].sudo().search([('name', '=', "Settings")])
        # set_admin = admin.users
        # loc va return
        check_meeting = []
        meeting_this_week = {}

        for calendar_attendee_this_week_item in calendar_attendee_this_week:
            meeting_today_am = []
            meeting_today_pm = []
            meeting_today = []
            index += 1
            meeting = calendar_attendee_this_week_item.event_id
            if self.user_has_groups('employee_time_table.group_admin_timetable') or self._uid == employee.user_id.id:
                meeting_reason = meeting.name
            else:
                meeting_reason = "Meeting Occupied"
            # fix time zone

            current_meeting_start = meeting.start.astimezone(timezone(self.get_timezone()))
            current_meeting_stop = meeting.stop.astimezone(timezone(self.get_timezone()))
            meeting_start_standard_visual = current_meeting_start.strftime("%d/%m/%Y %H:%M")
            meeting_stop_standard_visual = current_meeting_stop.strftime("%d/%m/%Y %H:%M")

            # if meeting not all day
            if not meeting.allday:
                # if no, check if meeting occurs in the morning, if yes, update data
                check_meeting.append(meeting.start.astimezone(timezone(self.get_timezone())).weekday())
                meeting_day = current_meeting_start.strftime("%A")
                if int(current_meeting_start.strftime("%H")) < 13 and int(current_meeting_stop.strftime("%H")) < 13:
                    # meeting_day += "_AM"
                    infos = [meeting_reason, meeting_start_standard_visual, meeting_stop_standard_visual]
                    meeting_today_am.append(True)
                    meeting_today_am.append(False)
                    meeting_today_am.append(meeting.id)
                    meeting_today_am.append(infos)
                    if not meeting_this_week.get(meeting_day):
                        meeting_this_week.update({
                            meeting_day: [True, False, index, [meeting_today_am]]
                        })
                    else:
                        new_meeting_today_data_am = meeting_this_week.get(meeting_day)[3]
                        new_meeting_today_data_am.append(meeting_today_am)
                        meeting_this_week.update({
                            meeting_day: [True, meeting_this_week.get(meeting_day)[1], index, new_meeting_today_data_am]
                        })

                elif int(current_meeting_start.strftime("%H")) >= 13 and int(current_meeting_stop.strftime("%H")) >= 13:
                    # meeting_day += "_PM"
                    infos = [meeting_reason, meeting_start_standard_visual, meeting_stop_standard_visual]
                    meeting_today_pm.append(False)
                    meeting_today_pm.append(True)
                    meeting_today_pm.append(meeting.id)
                    meeting_today_pm.append(infos)
                    if not meeting_this_week.get(meeting_day):
                        meeting_this_week.update({
                            meeting_day: [False, True, index, [meeting_today_pm]]
                        })
                    else:
                        new_meeting_today_data_pm = meeting_this_week.get(meeting_day)[3]
                        new_meeting_today_data_pm.append(meeting_today_pm)
                        meeting_this_week.update({
                            meeting_day: [meeting_this_week.get(meeting_day)[0], True, index, new_meeting_today_data_pm]
                        })
                else:
                    infos = [meeting_reason, meeting_start_standard_visual, meeting_stop_standard_visual]
                    meeting_today.append(True)
                    meeting_today.append(True)
                    meeting_today.append(meeting.id)
                    meeting_today.append(infos)
                    if not meeting_this_week.get(meeting_day):
                        meeting_this_week.update({
                            meeting_day: [True, True, index, [meeting_today]]
                        })
                    else:
                        new_meeting_today_data = meeting_this_week.get(meeting_day)[3]
                        new_meeting_today_data.append(meeting_today)
                        meeting_this_week.update({
                            meeting_day: [meeting_this_week.get(meeting_day)[0], True, index, new_meeting_today_data]
                        })
            else:
                current_meeting_start_tmp = meeting.start
                if datetime.strftime(current_meeting_start_tmp, '%Y/%m/%d') < datetime.strftime(start, '%Y/%m/%d'):
                    current_meeting_start_tmp = start
                # if not sunday
                monday_first_time = True
                while monday_first_time and current_meeting_start_tmp.weekday() < 7 and datetime.strftime(
                        current_meeting_start_tmp, '%Y/%m/%d') <= datetime.strftime(
                    meeting.stop, '%Y/%m/%d'):
                    current_meeting_day = current_meeting_start_tmp.strftime("%A")
                    check_meeting.append(current_meeting_start_tmp.weekday())
                    if not meeting_this_week.get(current_meeting_day):
                        meeting_this_week.update({
                            current_meeting_day: [True, True, index, [[True, True, meeting.id,
                                                                       [meeting_reason,
                                                                        meeting.start.strftime(
                                                                            "%d/%m/%Y") + ' 00:00',
                                                                        meeting.stop.strftime(
                                                                            "%d/%m/%Y") + ' 23:59']]]]
                        })
                    else:
                        meeting_this_week.get(current_meeting_day)[0] = True
                        meeting_this_week.get(current_meeting_day)[1] = True
                        meeting_this_week.get(current_meeting_day)[3].append([True, True, index, [meeting_reason,
                                                                                                  meeting.start.strftime(
                                                                                                      "%d/%m/%Y") + ' 00:00',
                                                                                                  meeting.stop.strftime(
                                                                                                      "%d/%m/%Y") + ' 23:59']])
                    index += 1
                    current_meeting_start_tmp += timedelta(days=1)
                    if current_meeting_start_tmp.weekday() == 0:
                        monday_first_time = False

        # if not having meeting, return false

        day_off = 'None'
        for i in range(6):
            if i not in check_meeting:
                if i == 0:
                    day_off = 'Monday'
                if i == 1:
                    day_off = 'Tuesday'
                if i == 2:
                    day_off = 'Wednesday'
                if i == 3:
                    day_off = 'Thursday'
                if i == 4:
                    day_off = 'Friday'
                if i == 5:
                    day_off = 'Saturday'
                meeting_today = []
                meeting_this_week.update({
                    day_off: [False, False, False, [meeting_today]]
                })
        return meeting_this_week, index


class UpdateDate(models.Model):
    _name = 'customer.change.create.date'

    def _default_employees(self):
        if self._context.get('active_ids'):
            return self.env['hr.employee'].browse(self._context.get('active_ids'))

    employee_ids = fields.Many2many('hr.employee', string="Employees", required=True,
                                    default=_default_employees)

    create_date_change = fields.Datetime(string="Change Created Date to")

    def mass_update(self):
        for rec in self.employee_ids:
            self.env.cr.execute(
                """UPDATE hr_employee SET create_date=%s WHERE id = %s""",
                [self.create_date_change, rec.id])
        return {'type': 'ir.actions.act_window_close'}
