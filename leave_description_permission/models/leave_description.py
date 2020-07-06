# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LeaveDescriptionPermission(models.Model):
    _inherit = 'hr.leave'

    def _read(self, fields):
        super(LeaveDescriptionPermission, self)._read(fields)
        if 'name' in fields and self.user_has_groups(
                'leave_description_permission.fix_hr_leave_process_group_user'):
            for record in self:
                try:
                    self.env.cr.execute('select name from hr_leave where id=%s', (record.id,))
                    current_record = self.env.cr.fetchone()
                    record._cache['name'] = current_record[0]
                except:
                    pass

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        for holiday in self:
            if holiday.user_has_groups(
                    'leave_description_permission.fix_hr_leave_process_group_user'):
                continue

    # def activity_update(self):
    #     for holiday in self:
    #         if holiday.state == 'confirm':
    #             holiday.activity_schedule(
    #                 'hr_holidays.mail_act_leave_approval',
    #                 user_id=holiday.employee_id.approve_leave_user.id)

    def _get_responsible_for_approval(self):
        if self.state == 'confirm' and self.employee_id.approve_leave_user:
            return self.employee_id.approve_leave_user
        elif self.state == 'confirm' and self.manager_id.user_id:
            return self.manager_id.user_id
        elif self.state == 'confirm' and self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.department_id.manager_id.user_id:
            return self.department_id.manager_id.user_id
        return self.env['res.users']

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        for rec in self:
            rec.can_approve = False
            if rec.env.uid == rec.employee_id.approve_leave_user.id and rec.user_has_groups(
                    'leave_description_permission.fix_hr_leave_process_group_user'):
                rec.can_approve = True
            elif rec.user_has_groups('hr_holidays.group_hr_holidays_manager'):
                rec.can_approve = True
            elif rec.create_uid.id == rec.env.uid and rec.user_has_groups(
                    'leave_description_permission.fix_hr_leave_process_group_user'):
                rec.can_approve = True

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_reset(self):
        for holiday in self:
            holiday.can_reset = False
            if holiday.create_uid.id == holiday.env.uid:
                holiday.can_reset = True
            elif holiday.user_has_groups('hr_holidays.group_hr_holidays_manager'):
                holiday.can_reset = True
            elif holiday.env.uid == holiday.employee_id.approve_leave_user.id and holiday.user_has_groups(
                    'leave_description_permission.fix_hr_leave_process_group_user'):
                holiday.can_reset = True


class EmployeeLeaveManager(models.Model):
    _inherit = 'hr.employee'

    approve_leave_user = fields.Many2one('res.users', string='User Will Approve Employee Leave',
                                         compute='_get_default_approve_leave_user', store=True)
    can_read_leave_users = fields.Many2many(
        'res.users', 'hr_employee_can_read_leave_users_rel', string="Employees Can Read Leave")

    @api.depends('parent_id')
    def _get_default_approve_leave_user(self):
        for rec in self:
            if not rec.approve_leave_user and rec.parent_id and rec.parent_id.user_id:
                rec.approve_leave_user = rec.parent_id.user_id.id
