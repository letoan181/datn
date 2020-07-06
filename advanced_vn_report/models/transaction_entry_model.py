from odoo import fields, models, api, _
from odoo.exceptions import UserError


class TransactionEntryModel(models.Model):
    _name = 'transaction.entry.model'
    _description = 'Kết chuyển chi phí hợp đồng'

    name = fields.Char()
    code = fields.Char(string="Mã", required=True, copy=False, default='N/A')
    date_from = fields.Date(string='Từ ngày ')
    date_to = fields.Date(string='Đến ngày')
    entry_lines = fields.Many2many('transaction.entry', string='Kết chuyển hợp đồng')
    state = fields.Selection(
        [('draft', 'New'), ('done', 'Posted')],
        'Trạng thái', readonly=True, copy=False, default='draft')
    count_move_line = fields.Integer('Bút toán liên quan', compute='compute_count_move_line')

    def compute_count_move_line(self):
        for rec in self:
            rec.count_move_line = 0
            move_lines = rec.env['account.move'].sudo().search([('transaction_entry_model_id', '=', self.id)])
            if move_lines:
                rec.count_move_line = len(move_lines)


    def load_transaction_lines(self):
        date_from = self.date_from
        date_to = self.date_to
        lines = self.env['transaction.entry'].sudo().search(
            [('date', '>=', date_from), ('date', '<=', date_to), ('state', '=', 'split')]).ids
        self.write({'entry_lines': [(6, 0, lines)]})
        # self.entry_lines= [(6, 0, lines)],

    # def cancel(self):
    #     for rec in self:
    #         rec.state = 'cancel'
    #         rec.entry_lines.update({'state': 'split'})

    def post_transaction_lines(self):
        for line in self.entry_lines:
            if line.state != 'split':
                raise UserError(_("Một dòng chưa được phân bổ hoặc đã được kết chuyển"))
        for line in self.entry_lines:
            account_move_lines = []
            if line.state == 'split':
                debit_line = {
                    'account_id': line.account_id.id,
                    'related_account_id': line.related_account_id.id,
                    'name': line.name,
                    'account_contract_id': line.contract_id.id,
                    'debit': line.price,
                }
                credit_line = {
                    'related_account_id': line.account_id.id,
                    'account_id': line.related_account_id.id,
                    'name': line.name,
                    'account_contract_id': line.contract_id.id,
                    'credit': line.price,
                }
                account_move_lines.append(debit_line)
                account_move_lines.append(credit_line)
            if not account_move_lines:
                pass
            else:
                account_move = self.env['account.move'].sudo().create({
                    'transaction_entry_model_id': self.id,
                    'transaction_entry_id': line.id,
                    'sale_order_contract_id': line.contract_id.sale_order_contract_id.id,
                    'account_contract_id': line.contract_id.id,
                    # 'ref': 'Kết chuyển chi phí giá thành hợp đồng kì từ ngày ' + self.date_from.strftime(
                    #     "%d-%m-%Y") + ' đến ngày ' + self.date_to.strftime("%d-%m-%Y"),
                    'ref': line.name,
                    'journal_id': self.env.ref('advanced_vn_report.transaction_entry_journal').id,
                    'line_ids': [(0, 0, account_move_line) for account_move_line in account_move_lines]
                })
                account_move.action_post()
                line.state = 'done'
        self.state = 'done'

    def action_view_transaction_entry_account_move(self):
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['domain'] = [('transaction_entry_model_id', '=', self.id)]
        return action

    @api.model
    def create(self, vals):
        entry = super(TransactionEntryModel, self).create(vals)
        if entry.code == _('N/A'):
            entry.code = self.env['ir.sequence'].next_by_code('advanced_vn_report.transaction_entry_sequence') or _('N/A')
        return entry
