from odoo import fields, models, api, _


class InheritInvite(models.TransientModel):
    _inherit = 'mail.wizard.invite'
