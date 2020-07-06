from odoo import models, fields, api


class InheritUser(models.Model):
    _inherit = 'res.users'
    independent = fields.Boolean(string='Independent')
    set_user_role = fields.Boolean(default=False)


