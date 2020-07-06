from odoo import api, fields, models
from datetime import date


class ReportTaskMissDeadline(models.Model):
    _name = "report.task.miss.deadline"
    _order = 'time_miss_deadline desc'

    project_id = fields.Many2one(string="Project", comodel_name="project.project")
    task_id = fields.Many2one(string="Task", comodel_name="project.task")
    user_id = fields.Many2one(string="Assigned to", comodel_name="res.users")
    department_id = fields.Many2one(string="Department", comodel_name="hr.department")
    date_deadline = fields.Date(string="Deadline")
    stage_id = fields.Many2one(string="Stage", comodel_name="project.task.type")
    code = fields.Char(string="Task code")
    priority = fields.Selection([(
        '1', 'Blocker'),
        ('2', 'Critical'),
        ('3', 'Important'),
        ('4', 'Normal'),
        ('5', 'Trivial')], string='Priority')
    project_manager = fields.Many2one(string="Project Manager", comodel_name="res.users")
    time_miss_deadline = fields.Float(string="Total time miss deadline")
    date_scan = fields.Date(string="Date scan")
