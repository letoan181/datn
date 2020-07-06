from odoo import fields, models


class AccountAssetInherit(models.Model):
    _inherit = 'account.asset'

    asset_code = fields.Char(string='Mã tài sản')

    def write(self, vals_list):
        asset = super(AccountAssetInherit, self).write(vals_list)
        if 'analytic_tag_ids' in vals_list and vals_list['analytic_tag_ids']:
            if self.depreciation_move_ids:
                for rec in self.depreciation_move_ids:
                    if rec.state == 'draft':
                        if rec.line_ids:
                            for line in rec.line_ids:
                                if line.debit > 0:
                                    line.analytic_tag_ids = vals_list['analytic_tag_ids']
        if 'account_analytic_id' in vals_list:
            account_analytic = self.env['account.analytic.account'].sudo().search(
                [('id', '=', vals_list['account_analytic_id'])])
            if self.depreciation_move_ids:
                for rec in self.depreciation_move_ids:
                    if rec.state == 'draft':
                        if rec.line_ids:
                            for line in rec.line_ids:
                                if line.debit > 0:
                                    line.analytic_account_id = account_analytic
        return asset
