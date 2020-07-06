# -*- coding: utf-8 -*-


import json

from odoo import api, fields, models, _
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = 'account.move'
    pre_journal_id = fields.Many2one('account.journal', string='Transfer To')

    # has_payments = fields.Boolean(compute="_compute_payment_ids",
    #                               help="Technical field used for usability purposes")
    date_last_payment_updated_at = fields.Datetime(string='Last Payment Updated At',
                                                   readonly=True, index=True)

    # @api.depends('matched_debit_ids', 'matched_credit_ids')
    # def _compute_payment_ids(self):
    #     for record in self:
    #         record.reconciled_invoice_ids = (
    #                 record.payment_move_line_ids.mapped('matched_debit_ids.debit_move_id.invoice_id') |
    #                 record.payment_move_line_ids.mapped(
    #                     'matched_credit_ids.credit_move_id.invoice_id'))
    #         record.has_payments = bool(record.reconciled_invoice_ids)
    #         if record.has_payments:
    #             new_write_date = record.payment_move_line_ids[
    #                 len(record.payment_move_line_ids) - 1].write_date
    #             if record.date_last_payment_updated_at != new_write_date:
    #                 record.sudo().write({
    #                     'date_last_payment_updated_at': record.payment_move_line_ids[
    #                         len(record.payment_move_line_ids) - 1].write_date
    #                 })

    def button_payments(self):
        views = [(self.env.ref('account.view_account_payment_tree').id, 'tree'),
                 (self.env.ref('account.view_account_payment_form').id, 'form')]
        return {
            'name': _('Paid Payments'),
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.payment_ids])],
        }

    # @api.multi
    # def action_invoice_open(self):
    #     post = super(AccountInvoice, self).action_invoice_open()
    #     for rec in self:
    #         if rec.type == 'in_invoice':
    #             account_move = self.env['account.move'].search(
    #                 [('use_estimate_money_flow', '=', True), ('payment_ref', '=', rec.id)])
    #             if len(account_move.ids) == 0:
    #                 account_move = self.env['account.move'].sudo().create({
    #                     'name': rec.number,
    #                     'date': date.today(),
    #                     'ref': rec.number,
    #                     'journal_id': rec.pre_journal_id.id,
    #                     'use_estimate_money_flow': True,
    #                     'payment_ref': rec.id
    #                 })
    #                 account_move_line = [{
    #                     'partner_id': rec.partner_id.id,
    #                     'account_id': rec.pre_journal_id.default_debit_account_id.id,
    #                     'debit': 0,
    #                     'credit': rec.amount_total,
    #                     'date': rec.date_invoice,
    #                     'date_maturity': rec.date_due,
    #                     'move_id': account_move.id,
    #                     'use_estimate_money_flow': True,
    #                     'currency_id': rec.currency_id.id,
    #                 }, {
    #                     'partner_id': rec.partner_id.id,
    #                     'account_id': rec.account_id.id,
    #                     'debit': rec.amount_total,
    #                     'credit': 0,
    #                     'date': rec.date_invoice,
    #                     'date_maturity': rec.date_due,
    #                     'move_id': account_move.id,
    #                     'use_estimate_money_flow': True,
    #                     'currency_id': rec.currency_id.id,
    #                 }]
    #                 self.env['account.move.line'].sudo().create(account_move_line)
    #         elif rec.type == 'out_invoice':
    #             account_move = self.env['account.move'].search(
    #                 [('use_estimate_money_flow', '=', True), ('payment_ref', '=', rec.id)])
    #             if len(account_move.ids) == 0:
    #                 account_move = self.env['account.move'].sudo().create({
    #                     'name': rec.number,
    #                     'date': date.today(),
    #                     'ref': rec.number,
    #                     'journal_id': rec.pre_journal_id.id,
    #                     'use_estimate_money_flow': True,
    #                     'payment_ref': rec.id
    #                 })
    #                 account_move_line = [{
    #                     'partner_id': rec.partner_id.id,
    #                     'account_id': rec.pre_journal_id.default_debit_account_id.id,
    #                     'debit': rec.amount_total,
    #                     'credit': 0,
    #                     'date': rec.date_invoice,
    #                     'date_maturity': rec.date_due,
    #                     'move_id': account_move.id,
    #                     'use_estimate_money_flow': True,
    #                     'currency_id': rec.currency_id.id,
    #                 }, {
    #                     'partner_id': rec.partner_id.id,
    #                     'account_id': rec.account_id.id,
    #                     'debit': 0,
    #                     'credit': rec.amount_total,
    #                     'date': rec.date_invoice,
    #                     'date_maturity': rec.date_due,
    #                     'move_id': account_move.id,
    #                     'use_estimate_money_flow': True,
    #                     'currency_id': rec.currency_id.id,
    #                 }]
    #                 self.env['account.move.line'].sudo().create(account_move_line)
    #     return post

    # @api.multi
    # def action_invoice_cancel(self):
    #     for rec in self:
    #         account_move = self.env['account.move'].search([('ref', '=', rec.number), ('state', '=', 'draft')])
    #         if len(account_move.ids) > 0:
    #             account_move.sudo().unlink()
    #     return super(AccountInvoice, self).action_invoice_cancel()

    def _get_outstanding_info_JSON(self):
        self.ensure_one()
        self.outstanding_credits_debits_widget = json.dumps(False)
        if self.state == 'open':
            # logan add use_estimate_money_flow = False
            domain = [('use_estimate_money_flow', '=', False),
                      ('account_id', '=', self.account_id.id),
                      ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id),
                      ('reconciled', '=', False),
                      '|',
                      '&', ('amount_residual_currency', '!=', 0.0), ('currency_id', '!=', None),
                      '&', ('amount_residual_currency', '=', 0.0), '&', ('currency_id', '=', None),
                      ('amount_residual', '!=', 0.0)]
            if self.type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': self.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = self.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == self.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        currency = line.company_id.currency_id
                        amount_to_show = currency._convert(abs(line.amount_residual), self.currency_id, self.company_id,
                                                           line.date or fields.Date.today())
                    if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                        continue
                    if line.ref:
                        title = '%s : %s' % (line.move_id.name, line.ref)
                    else:
                        title = line.move_id.name
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'title': title,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, self.currency_id.decimal_places],
                    })
                info['title'] = type_payment
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True

    related_sale_users_via_payment = fields.Many2many('res.users', 'account_move_sale_users_rel', 'account_move_id', 'user_id', string='Related Users Via Payment')
    related_single_sale_users_via_payment = fields.Many2one('res.users', string='Related Single User Via Payment', compute='_compute_related_single_sale_users_via_payment', store=True)

    @api.depends('line_ids')
    def _compute_related_single_sale_users_via_payment(self):
        for rec in self:
            rec.related_single_sale_users_via_payment = None
            try:
                if rec.type == 'entry' and rec.line_ids:
                    account_payment_ids = [e.payment_id for e in rec.line_ids]
                    if account_payment_ids and len(account_payment_ids) > 0:
                        related_sale_users_via_payment = []
                        for payment in account_payment_ids:
                            for invoice in payment.invoice_ids:
                                if invoice.invoice_user_id.id not in related_sale_users_via_payment:
                                    related_sale_users_via_payment.append(invoice.invoice_user_id.id)
                        if len(related_sale_users_via_payment) > 0:
                            rec.related_single_sale_users_via_payment = self.env['res.users'].sudo().browse(related_sale_users_via_payment[0])
                            self.env.cr.execute("""delete from account_move_sale_users_rel where account_move_id=%s""", (rec.id,))
                            for user in related_sale_users_via_payment:
                                self.env.cr.execute("""insert into account_move_sale_users_rel values (%s,%s)""", (rec.id, user))
            except Exception as ex:
                if ex and str(ex):
                    print('error _compute_related_single_sale_users_via_payment:' + str(ex))
