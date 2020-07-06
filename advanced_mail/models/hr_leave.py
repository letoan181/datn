# -*- coding: utf-8 -*-


from pytz import timezone, UTC
from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.tools.translate import _


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    def name_get(self):
        res = []
        for leave in self:

            if self.env.context.get('short_name'):
                if leave.leave_type_request_unit == 'hour':
                    res.append((leave.id, _(
                        "%s : %.2f hour(s) from " + str(leave.date_from.date()) + " at " + str(
                            leave.date_from.astimezone(timezone(self.env.user.tz)).time())[
                                                                                           0:5]) % (
                                    leave.name or leave.holiday_status_id.name, leave.number_of_hours_display)))
                else:
                    res.append((leave.id, _("%s : %.2f day(s) from " + str(
                        leave.date_from.astimezone(timezone(self.env.user.tz)).date())) % (
                                    leave.name or leave.holiday_status_id.name, leave.number_of_days)))
            else:
                if leave.holiday_type == 'company':
                    target = leave.mode_company_id.name
                elif leave.holiday_type == 'department':
                    target = leave.department_id.name
                elif leave.holiday_type == 'category':
                    target = leave.category_id.name
                else:
                    target = leave.employee_id.name
                if leave.leave_type_request_unit == 'hour':
                    res.append(
                        (leave.id,
                         _("%s on %s : %.2f hour(s) from " + str(leave.date_from.date()) + " at " + str(
                             leave.date_from.astimezone(timezone(self.env.user.tz)).time())[0:5]) %
                         (target, leave.holiday_status_id.name, leave.number_of_hours_display))
                    )
                else:
                    res.append(
                        (leave.id,
                         _("%s on %s : %.2f day(s) from " + str(leave.date_from.astimezone(timezone(self.env.user.tz)).date())) %
                         (target, leave.holiday_status_id.name, leave.number_of_days))
                    )
        return res

    def activity_update(self):
        to_clean, to_do = self.env['hr.leave'], self.env['hr.leave']
        for holiday in self:
            note = _('New %s Request created by %s from %s to %s') % (
                holiday.holiday_status_id.name, holiday.create_uid.name,
                fields.Datetime.to_string(holiday.date_from.astimezone(timezone(self.env.user.tz))),
                fields.Datetime.to_string(holiday.date_to.astimezone(timezone(self.env.user.tz))))
            if holiday.state == 'draft':
                to_clean |= holiday
            elif holiday.state == 'confirm':
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_approval',
                    note=note,
                    user_id=holiday.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif holiday.state == 'validate1':
                holiday.activity_feedback(['hr_holidays.mail_act_leave_approval'])
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_second_approval',
                    note=note,
                    user_id=holiday.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif holiday.state == 'validate':
                to_do |= holiday
            elif holiday.state == 'refuse':
                to_clean |= holiday
        if to_clean:
            to_clean.activity_unlink(
                ['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])
        if to_do:
            to_do.activity_feedback(
                ['hr_holidays.mail_act_leave_approval', 'hr_holidays.mail_act_leave_second_approval'])
