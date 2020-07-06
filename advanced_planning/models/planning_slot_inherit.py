# -*- coding: utf-8 -*-

from odoo import models, fields


class PlanningSendInherit(models.Model):
    _inherit = 'planning.slot'

    department_id = fields.Many2one(comodel_name='hr.department', related='employee_id.department_id', store=True)
    is_public = fields.Boolean(string='Public', default=False)
