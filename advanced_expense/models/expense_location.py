from odoo import models, fields, _


class ExpenseLocation(models.Model):
    _name = "expense.location"

    name = fields.Char(string=_("Address"))
