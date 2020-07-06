from odoo import api, models, fields


class Account(models.Model):
    _inherit = "account.account"

    is_profit_loss = fields.Boolean(default=False, string="Used in predicting cash flow")
