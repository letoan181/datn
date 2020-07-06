from odoo import api, fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    use_in_task_deadline = fields.Boolean(string="Use in task deadline reporting", default=True)

