from odoo import fields, models, api


class AccountMoveForceUpdateAmount(models.TransientModel):
    _name = "account.move.force.update.amount"

    def _default_account_move(self):
        if self._context.get('active_ids'):
            return self.env['account.move'].browse(self._context.get('active_ids'))

    account_moves = fields.Many2many('account.move',
                                     string="Record", required=True, default=_default_account_move)
    update_amount = fields.Float('New Amount', store=True, help='Update New Amount', digits=(16, 2))

    @api.model
    def default_get(self, fields):
        defaults = super(AccountMoveForceUpdateAmount, self).default_get(fields)
        default_account_move_id = self.env.context.get('default_account_move_id')
        if default_account_move_id:
            account_move_line = self.env['account.move.line'].sudo().search([('move_id', '=', default_account_move_id)])
            sample_update_amount = 0
            for e in account_move_line:
                if e['debit'] is not None and e['debit'] > e['credit'] and sample_update_amount == 0:
                    sample_update_amount = e['debit']
            defaults['update_amount'] = sample_update_amount
        return defaults

    def force_update_amount_now(self):
        self.env.cr.execute("""update account_move set amount_total_signed=%s where id=%s""",
                            (self.update_amount, self.account_moves.id,))
        self.env.cr.execute(
            """update account_move_line set debit=%s,balance=%s where debit > credit and move_id=%s""",
            (self.update_amount, self.update_amount, self.account_moves.id,))
        self.env.cr.execute(
            """update account_move_line set credit=%s,balance=%s where credit > debit and move_id=%s""",
            (self.update_amount, -self.update_amount, self.account_moves.id,))
        self.env.cr.execute(
            """update account_move_line set amount_residual=%s where debit > credit and move_id=%s and amount_residual_currency>0""",
            (self.update_amount, self.account_moves.id,))
        self.env.cr.execute(
            """update account_move_line set amount_residual=%s where credit > debit and move_id=%s and amount_residual_currency<0""",
            (-self.update_amount, self.account_moves.id,))
        # attendee = self.env['calendar.attendee'].sudo().search([('partner_id', '=', self.env['res.users'].sudo().browse(
        #     self._uid).partner_id.id), ('state', '!=', 'accepted'),
        #                                                         ('event_id', 'in', tuple(self.calendar_events.ids))])
        # if attendee:
        #     attendee.do_accept()
        # return {'type': 'ir.actions.act_window_close'}
        return {'type': 'ir.actions.client', 'tag': 'reload'}
