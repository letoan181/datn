from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    related_account_id = fields.Many2one('account.account', string='Related Account')
    account_contract_id = fields.Many2one('account.contract', string='Hợp đồng')


    asset_amount = fields.Monetary(related='asset_id.original_value', store=True)

