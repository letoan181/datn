from datetime import datetime, timedelta, date

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, tools, _


class Project(models.Model):
    _inherit = "project.project"

    the_total_amounts = fields.Float(string=_("Project Cost"), default=0)
    tm_dv_eh = fields.Float(string=_("Project Cost divided Effective Hours"), default=0, compute='_compute_amounts',
                            store=True)

    timeline_project = fields.One2many('project.timeline', 'project_id', string='TimeLine')
    branch_deadline = fields.Html(string='Deadline date', compute='_compute_get_branch_deadline')
    man_month = fields.Char(string='Man-Month', compute='_compute_man_month', compute_sudo=True)
    is_project_private = fields.Boolean(string="Is project private", default=False, groups="base.group_system")

    def _compute_man_month(self):
        for rec in self:
            total_man_timesheet = 0
            task = rec.env['project.task'].sudo().search([('project_id', '=', rec.id)])
            for result in task:
                contract = self.env['hr.contract'].sudo().search([('employee_id', '=', result.user_id.employee_id.name), ('state', '=', 'open')], limit=1)
                if contract:
                    if contract.type == 'partime' and contract.state == 'open':
                        total_man_timesheet += result.effective_hours / 2
                    else:
                        total_man_timesheet += result.effective_hours
            rec.man_month = round(total_man_timesheet / 8 / 22, 2)

    @api.depends('timeline_project')
    def _compute_get_branch_deadline(self):

        now = datetime.now()
        year = now.year
        statur = []
        sun = []
        saturday = date(year, 1, 1)
        saturday += timedelta(days=5 - saturday.weekday())
        sunday = date(year, 1, 1)
        sunday += timedelta(days=6 - sunday.weekday())
        # Get all saturday of year
        while saturday.year == year:
            saturday = saturday
            saturday += timedelta(days=7)
            statur.append(saturday)
        # Get all sunday of year
        while sunday.year == year:
            sunday = sunday
            sunday += timedelta(days=7)
            sun.append(sunday)
        # all sunday and saturday of year
        last_week = statur + sun
        for rec in self:
            work_day = []
            for line in rec.timeline_project:
                count = 0
                if line:
                    day_project = ((line.start_day + relativedelta(days=line.days) - fields.Date.today())).days
                    if line.type_day == 'bd':
                        # select all work day in branch project
                        for days in range(1, day_project):
                            # Select all day off in year
                            for day_off in last_week:
                                if line.start_day + relativedelta(days=days) == day_off:
                                    # count sunday and saturday of branch project
                                    count += 1
                        # day work for each branch of project
                        day_project = day_project + count
                    # description and day work for branch project
                    result = line.description + ":\t" + str(day_project) + "\t normal"
                    if line.project_invisible:
                        continue
                    work_day.append('<p>' + '--\t' + result + '</p>')
            time_deadline = '\t'.join(work_day)
            rec.branch_deadline = time_deadline

    @api.depends('the_total_amounts')
    def _compute_amounts(self):
        for record in self:
            record.tm_dv_eh = None
            if record._origin.id:
                self._cr.execute("""SELECT sum(effective_hours) FROM project_task WHERE project_id = %s""" % (
                    record._origin.id))
                res = self._cr.dictfetchone()
                if res['sum'] and res['sum'] != 0:
                    record.tm_dv_eh = record.the_total_amounts / res['sum']

    def filter_employee_follower_project(self):
        list_project = self.env['project.project'].search([])
        list_employee = []
        list_partner = []
        for project in list_project:
            for pas in project.message_partner_ids:
                if pas.employee:
                    list_employee.append(pas.id)
                else:
                    list_partner.append(pas.id)
            if list_partner:
                project.sudo().message_unsubscribe(partner_ids=list_partner)

    @api.model
    def create(self, vals_list):
        # auto create stage
        vals_list['privacy_visibility'] = 'employees'
        result = super(Project, self.sudo()).create(vals_list)
        result.write({
            'privacy_visibility': 'followers'
        })
        # resource = self.env.ref('project_advanced_report.advanced_project_stage_resource').id
        # todo = self.env.ref('project_advanced_report.advanced_project_stage_todo').id
        # qa = self.env.ref('project_advanced_report.advanced_project_stage_qa').id
        # done = self.env.ref('project_advanced_report.advanced_project_stage_done').id
        # self.env.cr.execute(
        #     """INSERT INTO project_task_type_rel (type_id, project_id) values (%s,%s),(%s,%s),(%s,%s),(%s,%s)""" %
        #     (str(resource), str(result.id), str(todo), str(result.id), str(qa), str(result.id),
        #           str(done), str(result.id), ))
        stage_list = [{
            'name': 'Resource',
            'stage_type': 'resource',
            'sequence': 1,
            'project_ids': [(4, result.id)]
        }, {
            'name': 'Todo',
            'stage_type': 'todo',
            'sequence': 2,
            'project_ids': [(4, result.id)]
        }, {
            'name': 'In Progress',
            'stage_type': 'todo',
            'sequence': 3,
            'project_ids': [(4, result.id)]
        }, {
            'name': 'QA',
            'stage_type': 'qa',
            'sequence': 4,
            'project_ids': [(4, result.id)]
        }, {
            'name': 'Done',
            'stage_type': 'done',
            'sequence': 5,
            'project_ids': [(4, result.id)]
        }]
        self.env['project.task.type'].sudo().create(stage_list)
        return result


class Task(models.Model):
    _inherit = "project.task"
    stage_type_text = fields.Integer(string='Stage Type', default=2, help="Update stage type.", index=True, store=True)
    project_message_user_ids = fields.Many2many(
        comodel_name='res.users', string='Followers (Users)',
        compute='_compute_project_message_user_ids', compute_sudo=True, store=False)

    def view_all_task_project(self):
        action_id = self.env.ref('project.act_project_project_2_project_task_all').id
        menu_id = self.env.ref('project.menu_main_pm').id

        return {
            'type': 'ir.actions.act_url',
            'url': '/web#action=' + str(action_id) + '&active_id=' + str(
                self.id) + '&model=project.task&view_type=kanban&cids=1&menu_id=' + str(menu_id),
            'target': 'self',
        }

    @api.depends('project_id')
    def _compute_project_message_user_ids(self):
        for rec in self:
            message_partner_ids = rec.sudo().project_id.message_partner_ids
            rec.sudo().project_message_user_ids = []
            if len(message_partner_ids) > 0:
                rec.sudo().project_message_user_ids = self.env['res.users'].sudo().search(
                    [('partner_id', 'in', tuple(e for e in message_partner_ids.ids))])

    @api.depends('stage_id')
    def _update_stage_type_text(self):
        for record in self:
            if record.stage_id.stage_type == 'resource':
                record.stage_type_text = 1
            elif record.stage_id.stage_type == 'todo':
                record.stage_type_text = 2
            elif record.stage_id.stage_type == 'qa':
                record.stage_type_text = 3
            elif record.stage_id.stage_type == 'done':
                record.stage_type_text = 4

    @api.depends('effective_hours', 'amounts_per_hour', 'project_id.the_total_amounts')
    def _amounts_get(self):
        for record in self:
            record.amounts_per_hour = 0
            record.avg_amounts_per_task = record.project_id.the_total_amounts
            self._cr.execute(
                """SELECT count(project_id) FROM project_task WHERE project_id = %s""" % (
                    record.project_id.id if record.project_id.id else -1))
            res = self._cr.dictfetchone()
            if res['count'] != 0:
                if len(record.project_id.tasks) != 0:
                    record.avg_amounts_per_task = record.project_id.the_total_amounts / res['count']
                record.amounts_per_hour = (record.project_id.tm_dv_eh / res['count'])

    amounts_per_hour = fields.Float(compute='_amounts_get', store=True, string=_("Cost per hour"),
                                    help=_("Computed as : project_id.the_total_amounts/effective_hours"))

    avg_amounts_per_task = fields.Float(compute='_amounts_get', store=True, string=_("Average Cost per Task"),
                                        help=_("Computed as : project_id.the_total_amounts / len(project_id.tasks)"))

    predict_date_start = fields.Date(string='Predict Starting Date',
                                     default=fields.Date.today,
                                     index=True, copy=False)
    # computed_deadline_for_calendar = fields.Date(string='Predict Starting Date', index=True, copy=False,
    #                                              compute='_compute_computed_deadline_for_calendar', store=True)

    compute_predict_date_start_calendar = fields.Datetime('Start', compute="_compute_date",
                                                          inverse="_inverse_predict_deadline_dates", store=True)
    compute_stop_date_deadline_calendar = fields.Datetime('Stop', compute="_compute_date",
                                                          inverse="_inverse_predict_deadline_dates", store=True)

    # date_deadline = fields.Date(string='Deadline',
    #                             inverse="_inverse_start_stop_dates",
    #                             index=True, copy=False, tracking=True)

    # inverse predict date va date deadline cho predict date calendar va date deadline calendar

    @api.depends('predict_date_start', 'date_deadline')
    def _compute_date(self):
        for task in self:
            task.compute_predict_date_start_calendar = None
            task.compute_stop_date_deadline_calendar = None
            if task.predict_date_start:
                task.compute_predict_date_start_calendar = task.predict_date_start
            if task.date_deadline:
                task.compute_stop_date_deadline_calendar = task.date_deadline + relativedelta(days=1, hours=-8)

    # inverse predict date, date deadline cho predict date calendar, date deadline calendar
    def _inverse_predict_deadline_dates(self):
        for task in self:
            if task.compute_predict_date_start_calendar:
                task.sudo().write(
                    {'predict_date_start': task.compute_predict_date_start_calendar + relativedelta(hours=7)})
                task.compute_predict_date_start_calendar = task.predict_date_start
            if task.compute_stop_date_deadline_calendar:
                task.sudo().write({'date_deadline': task.compute_stop_date_deadline_calendar + relativedelta(hours=7)})
                task.compute_stop_date_deadline_calendar = task.date_deadline + relativedelta(days=1, hours=-8)

    # @api.depends('date_deadline')
    # def _compute_computed_deadline_for_calendar(self):
    #     for rec in self:
    #         rec.computed_deadline_for_calendar = rec.date_deadline
    #         if rec.date_deadline:
    #             rec.computed_deadline_for_calendar = rec.date_deadline + timedelta(days=1)

    # update predict, deadline date calendar cho nhung task khong co
    def cron_job_update_predict_deadline_date_calendar(self):
        all_project_task = self.env['project.task'].sudo().search(
            [('compute_predict_date_start_calendar', '=', False), ('compute_stop_date_deadline_calendar', '=', False)])
        if all_project_task:
            for rec in all_project_task:
                rec.compute_predict_date_start_calendar = 0
                rec.compute_stop_date_deadline_calendar = 0
                if rec.predict_date_start and rec.date_deadline:
                    rec.compute_predict_date_start_calendar = rec.predict_date_start
                    rec.compute_stop_date_deadline_calendar = rec.date_deadline

    @api.onchange('predict_date_start', 'date_deadline')
    def _update_deadline(self):
        for record in self:
            if not record.date_deadline:
                record.date_deadline = datetime.now().strftime('%Y-%m-%d')
            if record.predict_date_start:
                if record.date_deadline < record.predict_date_start:
                    record.date_deadline = record.predict_date_start

    @api.model
    def create(self, vals_list):
        if vals_list.get('stage_id'):
            current_stage = self.env['project.task.type'].sudo().browse(vals_list.get('stage_id'))
            if current_stage.stage_type == 'resource':
                vals_list['stage_type_text'] = 1
            elif current_stage.stage_type == 'todo':
                vals_list['stage_type_text'] = 2
            elif current_stage.stage_type == 'qa':
                vals_list['stage_type_text'] = 3
            elif current_stage.stage_type == 'done':
                vals_list['stage_type_text'] = 4
        result = super(Task, self).create(vals_list)
        return result

    def write(self, vals):
        if vals.get('stage_id'):
            # check permission, if not admin, not project manager, not owner raise error
            # can_update_task = False
            # if self.env.user.has_group('base.group_system') or self.user_id.id == self._uid or self.project_id.user_id.id == self._uid:
            #     can_update_task = True
            # if not can_update_task:
            #     raise UserError(_("You can not update tasks of other people"))
            current_stage = self.env['project.task.type'].sudo().browse(vals.get('stage_id'))
            if current_stage.stage_type == 'resource':
                vals['stage_type_text'] = 1
            elif current_stage.stage_type == 'todo':
                vals['stage_type_text'] = 2
            elif current_stage.stage_type == 'qa':
                vals['stage_type_text'] = 3
            elif current_stage.stage_type == 'done':
                vals['stage_type_text'] = 4
        result = super(Task, self).write(vals)

        return result

    effective_hours_for_customer = fields.Float("Hours Spent")


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    total_amounts = fields.Float(_("Total Cost"), readonly=True)
    amounts_per_hour = fields.Float(_("Total Cost / Effective Hours"), readonly=True)
    filter_tasks = fields.Boolean()

    def _select(self):
        return super(ReportProjectTaskUser, self)._select() + """,
                t.avg_amounts_per_task as total_amounts,
                t.amounts_per_hour as amounts_per_hour,
                t.active as filter_tasks"""

    def _group_by(self):
        return super(ReportProjectTaskUser, self)._group_by() + """,
                t.amounts_per_hour,
                t.avg_amounts_per_task"""

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
               CREATE view %s as
                 %s
                 FROM project_task t
                   %s
           """ % (self._table, self._select(), self._group_by()))


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    stage_type = fields.Selection([
        ('resource', 'Resource'),
        ('todo', 'Todo'),
        ('qa', 'QA'),
        ('done', 'Done')
    ], string='Stage Type', required=True, track_visibility='always', default='todo',
        help="Set stage type.")

    def write(self, vals):
        result = super(ProjectTaskType, self).write(vals)
        if vals.get('stage_type'):
            new_stage_type_text = 1
            if vals.get('stage_type') == 'resource':
                new_stage_type_text = 1
            elif vals.get('stage_type') == 'todo':
                new_stage_type_text = 2
            elif vals.get('stage_type') == 'qa':
                new_stage_type_text = 3
            elif vals.get('stage_type') == 'done':
                new_stage_type_text = 4
            self.env['project.task'].sudo().search([('stage_id', 'in', tuple(self.ids))]).write({
                'stage_type_text': new_stage_type_text
            })
        return result
