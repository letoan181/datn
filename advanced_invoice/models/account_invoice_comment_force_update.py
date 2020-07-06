from odoo import fields, models, api


class AccountInvoiceForceUpdateComment(models.TransientModel):
    _name = "account.move.force.update.comment"

    def _default_account_invoice(self):
        if self._context.get('active_ids'):
            return self.env['account.move'].browse(self._context.get('active_ids'))

    account_invoices = fields.Many2many('account.move',
                                        string="Record", required=True, default=_default_account_invoice)
    comment = fields.Text('New Comment')

    def force_update_comment_now(self):
        self.ensure_one()
        current_account_invoice = self.env['account.move'].browse(self.account_invoices.id)
        initial_values = {current_account_invoice.id: {'comment': current_account_invoice.comment}}
        current_account_invoice.comment = self.comment
        current_account_invoice.message_track(current_account_invoice.fields_get(['comment']), initial_values)
        self.env.cr.execute("""update account_invoice set comment=%s where id=%s""",
                            (self.comment, self.account_invoices.id,))
        self.env.cr.execute("""delete from ir_attachment where res_model like 'account.move' and res_id=%s""",
                            (self.account_invoices.id,))
        return {'type': 'ir.actions.act_window_close'}
        # return {'type': 'ir.actions.client', 'tag': 'reload'}
