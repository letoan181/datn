# -*- coding: utf-8 -*-

from odoo import models, fields


class UserType(models.Model):
    _inherit = 'res.users'

    project_user_type = fields.Selection(string="Project Uer Type",
                                         selection=[('employee', 'Employee'), ('vendor', 'Vendor'),
                                                    ('customer', 'Customer')], default="employee")
