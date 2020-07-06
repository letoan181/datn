from odoo import models, fields


class IntangibleAssetsProcess(models.Model):
    _inherit = 'hr.employee'

    intangible_ids = fields.Many2many(comodel_name="intangible.asset", string="Virtual Assets", )
