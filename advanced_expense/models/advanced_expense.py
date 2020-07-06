# -*- coding: utf-8 -*-

from odoo import models, fields, _


class AdvancedExpense(models.Model):
    _inherit = "hr.expense"

    expense_type = fields.Selection([
        ('common', 'Common'),
        ('special', 'Special'),
    ], string='Type', help="Conditional Set To Approval", default='common', required=True)
    expense_location = fields.Many2one("expense.location", String=_("Expense Location"), required=True)
