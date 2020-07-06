from odoo import api, models, fields


class ProjectTimeLine(models.Model):
    _name = 'project.timeline'
    _order = 'start_day asc'
    description = fields.Char(string='Description for project', required=True)
    start_day = fields.Date(string='Start Day', required=True)
    days = fields.Integer(string='Days')
    type_day = fields.Selection([
        ('nd', 'Normal Day'),
        ('bd', 'Business Day'),
    ], default='nd', string="Day Type")
    project_id = fields.Many2one('project.project', string='ProjectID')
    project_invisible = fields.Boolean(string='Invisible')
