# -*- coding: utf-8 -*-

from odoo import models, fields


class AdvancedExpense(models.Model):
    _inherit = "hr.expense.sheet"

    advanced_date_due = fields.Date(string='Due Date', default=fields.Date.today(), required=True)
