from odoo import api, fields, models
from datetime import date, datetime
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang


class ReportTaskMissDeadlinePopup(models.TransientModel):
    _name = "report.miss.deadline.popup"

    type = fields.Selection(string="Type report",
                            selection=[('project', 'Project'), ('department', 'Department'),
                                       ('employee', 'Employee'), ('project_and_department', 'Project and Department'),
                                       ('project_and_employee', 'Project and Employee'),
                                       ('department_and_employee', 'Department and Employee'), ('all', 'All')])
    project_ids = fields.Many2many(string="Projects", comodel_name="project.project")
    department_ids = fields.Many2many(string="Department_ids", comodel_name="hr.department")
    user_ids = fields.Many2many(string="Employee_ids", comodel_name="res.users")
    date_scan = fields.Date(string="Date Scan", default=date.today())
    # config_ids = fields.Many2many(string="Exception stage", comodel_name="config.stage.report.deadline")

    def gen_report(self):
        task_ids = self.env['project.task']
        if self.type == 'project' and self.project_ids:
            task_ids = self.env['project.task'].sudo().search(
                [('project_id', 'in', self.project_ids.ids), ('date_deadline', '<=', self.date_scan)])
            task_ids = self.remove_task_have_stage_not_in_report(task_ids=task_ids)
        if self.type == 'department' and self.department_ids:
            employee_of_department = []
            for department in self.department_ids:
                if department.member_ids:
                    for employee in department.member_ids:
                        if employee.user_id:
                            employee_of_department.append(employee.user_id.id)
            task_ids = self.env['project.task'].sudo().search(
                [('user_id', 'in', employee_of_department), ('date_deadline', '<=', self.date_scan)])
            task_ids = self.remove_task_have_stage_not_in_report(task_ids=task_ids)

        if self.type == 'employee' and self.user_ids:
            task_ids = self.env['project.task'].sudo().search(
                [('user_id', 'in', self.user_ids.ids), ('date_deadline', '<=', self.date_scan)])
            task_ids = self.remove_task_have_stage_not_in_report(task_ids=task_ids)

        if self.type == 'project_and_department' and self.department_ids and self.project_ids:
            employee_of_department = []
            for department in self.department_ids:
                if department.member_ids:
                    for employee in department.member_ids:
                        if employee.user_id:
                            employee_of_department.append(employee.user_id.id)
            task_ids = self.env['project.task'].sudo().search(
                [('user_id', 'in', employee_of_department), ('project_id', 'in', self.project_ids.ids),
                 ('date_deadline', '<=', self.date_scan)])
            task_ids = self.remove_task_have_stage_not_in_report(task_ids=task_ids)

        if self.type == 'project_and_employee' and self.user_ids and self.project_ids:
            task_ids = self.env['project.task'].sudo().search(
                [('user_id', 'in', self.user_ids.ids), ('project_id', 'in', self.project_ids.ids),
                 ('date_deadline', '<=', self.date_scan)])
            task_ids = self.remove_task_have_stage_not_in_report(task_ids=task_ids)

        if self.type == 'department_and_employee' and self.user_ids and self.department_ids:
            employee_of_department = []
            for department in self.department_ids:
                if department.member_ids:
                    for employee in department.member_ids:
                        if employee.user_id:
                            employee_of_department.append(employee.user_id.id)
            task_ids = self.env['project.task'].sudo().search(
                [('user_id', 'in', self.user_ids.ids), ('department_ids', 'in', employee_of_department),
                 ('date_deadline', '<=', self.date_scan)])
            task_ids = self.remove_task_have_stage_not_in_report(task_ids=task_ids)
        if self.type == 'all' and self.user_ids and self.department_ids and self.project_ids:
            employee_of_department = []
            for department in self.department_ids:
                if department.member_ids:
                    for employee in department.member_ids:
                        if employee.user_id:
                            employee_of_department.append(employee.user_id.id)
            task_ids = self.env['project.task'].sudo().search(
                [('user_id', 'in', self.user_ids.ids), ('user_id', 'in', employee_of_department),
                 ('project_id', 'in', self.project_ids.ids),
                 ('date_deadline', '<=', self.date_scan)])
            task_ids = self.remove_task_have_stage_not_in_report(task_ids=task_ids)
        if task_ids:
            for task in task_ids:
                employee = self.env['hr.employee'].sudo().search([('user_id', '=', task.user_id.id)], limit=1)
                department = False
                if employee.department_id:
                    department = employee.department_id.id
                duration = self.date_scan - task.date_deadline
                self.env['report.task.miss.deadline'].sudo().create({
                    'project_id': task.project_id.id,
                    'project_manager': task.project_id.user_id.id,
                    'task_id': task.id,
                    'code': task.code,
                    'user_id': task.user_id.id,
                    'department_id': department,
                    'date_deadline': task.date_deadline,
                    'stage_id': task.stage_id.id,
                    'priority': task.priority,
                    'time_miss_deadline': duration.days,
                    'date_scan': self.date_scan,

                })
        tree_view_id = self.env.ref('project_advanced_report.report_task_miss_deadline_view_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'name': 'Report Task Miss Deadline',
            'res_model': 'report.task.miss.deadline',
            'domain': [('date_scan', '=', self.date_scan)],
            'target': 'main',
            # 'context': context,
        }
        return action

    def remove_task_have_stage_not_in_report(self, task_ids=None):
        res = task_ids
        if task_ids:
            for task in task_ids:
                if not task.stage_id.use_in_task_deadline:
                    res -= task
        return res
