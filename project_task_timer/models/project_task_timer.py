from datetime import datetime

from odoo import models, fields, _


class ProjectTaskTimeSheet(models.Model):
    _inherit = 'account.analytic.line'

    date_start = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='End Date', readonly=1)
    timer_duration = fields.Float(invisible=1, string='Time Duration (Minutes)')
    employee_location = fields.Many2one(comodel_name='company.location', strings='Location',
                                        related='employee_id.employee_location', store=True)
    employee_category_ids = fields.Many2many(related='employee_id.category_ids', string="Employee Tags", readonly=False,
                                             related_sudo=False)
    # department leader user
    team_leader_user_id = fields.Many2one('res.users', related='employee_id.department_id.manager_id.user_id', store=True)


class ProjectTaskTimer(models.Model):
    _inherit = 'project.task'

    task_timer = fields.Boolean()
    task_timer_string = fields.Char(compute='_compute_task_timer_string')
    is_my_task = fields.Boolean(compute='_compute_is_my_task')
    is_user_working = fields.Boolean(
        'Is Current User Working',
        help="Technical field indicating whether the current user is working. ")
    # duration = fields.Float(
    #     'Real Duration', compute='_compute_duration',
    #     store=True)
    duration = fields.Float(
        'Real Duration', store=True)

    # def _compute_is_user_working(self):
    #     for order in self:
    #         if order.timesheet_ids.filtered(lambda x: (not x.date_end) and (x.date_start)):
    #             order.is_user_working = True
    #         else:
    #             order.is_user_working = False

    def cron_job_stop_all_task_timer(self):
        last_working_tasks = self.env['account.analytic.line'].sudo().search(
            [('date_start', '!=', False), ('date_end', '=', False)])
        for e in last_working_tasks:
            try:
                unit_amount = 0.0
                timer_duration = 0.0
                if e.date_start:
                    diff = fields.Datetime.now() - e.date_start
                    timer_duration = round(diff.total_seconds() / 60.0, 2)
                    unit_amount = round(diff.total_seconds() / (60.0 * 60.0), 2)
                e.write({
                    'date_end': fields.Datetime.now(),
                    'unit_amount': unit_amount,
                    'timer_duration': timer_duration,
                })
                if e.task_id:
                    e.task_id.write({
                        'is_user_working': False,
                        'task_timer': False
                    })
            except Exception as ex:
                print('error_cron_job_stop_all_task_timer')
                a = 0

    def _compute_task_timer_string(self):
        for rec in self:
            rec.task_timer_string = ''
            if not rec.task_timer:
                rec.task_timer_string = '---> Start'
            else:
                rec.task_timer_string = 'Stop <---'

    def _compute_is_my_task(self):
        for rec in self:
            if self._uid == rec.user_id.id or self.user_has_groups('base.group_system'):
                rec.is_my_task = True
            else:
                rec.is_my_task = False

    def toggle_start(self):
        for record in self:
            record.task_timer = not record.task_timer
        if self.task_timer:
            ### end last task
            last_working_tasks = self.env['account.analytic.line'].search(
                [('date_start', '!=', False), ('date_end', '=', False), ('create_uid', '=', self._uid)])
            for e in last_working_tasks:
                unit_amount = 0.0
                timer_duration = 0.0
                if e.date_start:
                    diff = fields.Datetime.now() - e.date_start
                    timer_duration = round((diff.total_seconds()) / 60.0, 2)
                    unit_amount = round((diff.total_seconds()) / (60.0 * 60.0), 2)
                e.write({
                    'date_end': fields.Datetime.now(),
                    'unit_amount': unit_amount,
                    'timer_duration': timer_duration
                })
                e.task_id.write({
                    'is_user_working': False
                })
            ### end last task
            self.write({'is_user_working': True})
            time_line = self.env['account.analytic.line']
            for time_sheet in self:
                time_line.create({
                    'name': self.env.user.name + ': ' + time_sheet.name,
                    'task_id': time_sheet.id,
                    'user_id': self.env.user.id,
                    'project_id': time_sheet.project_id.id,
                    'date_start': datetime.now(),
                })
        else:
            self.write({'is_user_working': False})
            time_line_obj = self.env['account.analytic.line']
            domain = [('task_id', 'in', self.ids), ('date_end', '=', False), ('create_uid', '=', self._uid)]
            for time_line in time_line_obj.search(domain):
                if time_line.date_start:
                    time_line.write({'date_end': fields.Datetime.now()})
                    if time_line.date_end:
                        diff = time_line.date_end - time_line.date_start
                        time_line.timer_duration = round(diff.total_seconds() / 60.0, 2)
                        time_line.unit_amount = round(diff.total_seconds() / (60.0 * 60.0), 2)
                    else:
                        time_line.unit_amount = 0.0
                        time_line.timer_duration = 0.0
        if self.task_timer:
            message = 'Start timesheet success!!'
            view_form = self.env.ref('project_task_timer.time_sheet_notes').id

            return {
                'name': _('Message'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'notes.views',
                'views': [(view_form, 'form')],
                'view_id': view_form,
                'target': 'new',
                'context': {'default_message_task': message},
            }
        else:
            message = 'Stop timesheet success!!'
            view_form = self.env.ref('project_task_timer.time_sheet_notes').id
            return {
                'name': _('Message'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'notes.views',
                'views': [(view_form, 'form')],
                'view_id': view_form,
                'target': 'new',
                'context': {'default_message_task': message},
            }


class ProjectTaskTimerView(models.TransientModel):
    _name = 'notes.views'

    # def toggle_start(self):
    #     res = super(ProjectTaskTimerView, self)._toggle_start()
    #
    #     for rec in self:
    #         if rec.task_timer:
    #             message = 'Timesheet Success'
    #             view_form = self.env.ref('project_task_timer.time_sheet_notes').id
    #             return {
    #                 'name': _('Message'),
    #                 'type': 'ir.actions.act_window',
    #                 'view_mode': 'form',
    #                 'res_model': 'notes.views',
    #                 'views': [(view_form, 'form')],
    #                 'view_id':view_form,
    #                 'res_id':self.id,
    #                 'target': 'new',
    #                 'context': {'default_name': message},
    #             }

    message_task = fields.Char('Message')
