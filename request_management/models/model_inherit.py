from odoo import models, fields


class AdvancedInheritResPartner(models.Model):
    _inherit = 'hr.employee'

    request_id = fields.One2many('advanced.request.management', 'assign_to', string='Assigned to')
    employee_id = fields.One2many('advanced.request.detail', 'employee_id', string='Employee')
    employee_ids = fields.One2many('advanced.request.management', 'employee', string='Employee')
