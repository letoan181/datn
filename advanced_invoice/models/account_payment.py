# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    team_id = fields.Many2one('crm.team', string='Sale Team (Location)', store=True)
    estimate_receiver_amount = fields.Monetary('Computed Receiver Amount (Exclude Payment Fee)',
                                               compute='_compute_estimate_receiver_amount',
                                               store=True,
                                               help='Balance as calculated based on Payment Amount and Currency',
                                               currency_field='destination_currency_id', track_visibility='always',
                                               digits=(16, 2))

    estimate_sender_amount = fields.Monetary('Computed Sender Amount', compute='_compute_estimate_sender_amount',
                                             store=True,
                                             help='Balance as calculated based on Payment Amount and Currency',
                                             currency_field='sender_currency_id', track_visibility='always',
                                             digits=(16, 2))

    sender_currency_id = fields.Many2one("res.currency", string="Sender Currency", readonly=True)
    currency_rate_ref = fields.Float("# Ref Sender Currency Rate", store=True, digits=(12, 6),
                                     help='The rate of the currency',
                                     compute='_compute_new_currency_rate_ref')
    currency_rate = fields.Float("Sender Currency Rate", store=True, digits=(12, 6), help='The rate of the currency',
                                 default=False, required=True)
    destination_currency_id = fields.Many2one("res.currency", string="Destination Currency", readonly=True)
    destination_currency_rate_ref = fields.Float("# Ref Destination Currency Rate", store=True, digits=(12, 6),
                                                 help='The rate of the destination currency',
                                                 compute='_compute_new_destination_currency_rate_ref')

    destination_currency_rate = fields.Float("Destination Currency Rate", store=True, digits=(12, 6),
                                             help='The rate of the destination currency', default=False, required=True)
    payment_currency_rate_ref = fields.Float("# Ref Payment Currency Rate", store=True, digits=(12, 6),
                                             help='The rate of the payment currency',
                                             compute='_compute_new_payment_currency_rate_ref')

    payment_currency_rate = fields.Float("Payment Currency Rate", store=True, digits=(12, 6),
                                         help='The rate of the payment currency', default=False, required=True)

    # additional field for bank fee
    destination_bank_fee = fields.Float("Destination Payment Fee", store=True, digits=(12, 6),
                                        help='Bank Fee', default=False)
    expect_destination_amount = fields.Float("Expected Destination Net Amount", store=True, digits=(12, 6),
                                             help='Expected destination amount', default=False)
    expected_destination_currency_rate = fields.Float("-> Expected Destination Currency Rate", store=True,
                                                      digits=(12, 6),
                                                      help='The rate of the currency',
                                                      compute='_compute_new_currency_rate_by_expected_cost')
    # additional field for expense
    current_hr_expense_id = fields.Many2one("hr.expense", String=_("###Expense"), readonly=True)

    def _onchange_currency(self):
        return

    @api.depends('amount', 'currency_id', 'payment_currency_rate', 'destination_journal_id',
                 'destination_currency_rate')
    def _compute_estimate_receiver_amount(self):
        for rec in self:
            rec.estimate_receiver_amount = 0
            if rec.payment_currency_rate > 0:
                rec.estimate_receiver_amount = rec.amount / rec.payment_currency_rate * rec.destination_currency_rate

    @api.depends('amount', 'currency_id', 'payment_currency_rate', 'journal_id', 'currency_rate')
    def _compute_estimate_sender_amount(self):
        for rec in self:
            rec.estimate_sender_amount = 0
            if rec.payment_currency_rate > 0:
                rec.estimate_sender_amount = rec.amount / rec.payment_currency_rate * rec.currency_rate

    @api.depends('journal_id')
    def _compute_new_currency_rate_ref(self):
        for rec in self:
            if len(rec.journal_id) > 0:
                currency_ids = rec.journal_id[0]['currency_id'].ids
                if len(currency_ids) > 0:
                    rec.currency_id = rec.journal_id[0]['currency_id'].ids[0]
                    rec.currency_rate_ref = \
                        self.env['res.currency.rate'].sudo().search(
                            [('currency_id', '=', rec.currency_id.id)])[0][
                            'rate']
                else:
                    rec.currency_id = self.env['res.users'].sudo().browse(self._uid).company_id.currency_id.id
                    rec.currency_rate_ref = \
                        self.env['res.currency.rate'].sudo().search(
                            [('currency_id', '=', rec.currency_id.id)])[0][
                            'rate']
                rec.currency_rate = rec.currency_rate_ref

    @api.depends('destination_journal_id')
    def _compute_new_destination_currency_rate_ref(self):
        for rec in self:
            if len(rec.destination_journal_id) > 0:
                currency_ids = rec.destination_journal_id[0]['currency_id'].ids
                if len(currency_ids) > 0:
                    rec.destination_currency_id = rec.destination_journal_id[0]['currency_id'].ids[0]
                    rec.destination_currency_rate_ref = \
                        self.env['res.currency.rate'].sudo().search(
                            [('currency_id', '=', rec.destination_currency_id.id)])[0][
                            'rate']
                else:
                    rec.destination_currency_id = self.env['res.users'].sudo().browse(self._uid).company_id.currency_id.id
                    rec.destination_currency_rate_ref = \
                        self.env['res.currency.rate'].sudo().search(
                            [('currency_id', '=', rec.destination_currency_id.id)])[0][
                            'rate']
                rec.destination_currency_rate = rec.destination_currency_rate_ref

    @api.depends('currency_id')
    def _compute_new_payment_currency_rate_ref(self):
        for rec in self:
            if len(rec.currency_id) > 0:
                rate = self.env['res.currency.rate'].sudo().search(
                    [('currency_id', '=', rec.currency_id.id)])[0][
                    'rate']
                rec.payment_currency_rate_ref = rate
                rec.payment_currency_rate = rate

    @api.depends('journal_id')
    def _compute_new_currency_rate_ref(self):
        for rec in self:
            if len(rec.journal_id) > 0:
                currency_ids = rec.journal_id[0]['currency_id'].ids
                if len(currency_ids) > 0:
                    rec.sender_currency_id = rec.journal_id[0]['currency_id'].ids[0]
                    rec.currency_rate_ref = \
                        self.env['res.currency.rate'].sudo().search(
                            [('currency_id', '=', rec.sender_currency_id.id)])[0][
                            'rate']
                else:
                    rec.sender_currency_id = self.env['res.users'].sudo().browse(self._uid).company_id.currency_id.id
                    rec.currency_rate_ref = \
                        self.env['res.currency.rate'].sudo().search(
                            [('currency_id', '=', rec.sender_currency_id.id)])[0][
                            'rate']
                rec.currency_rate = rec.currency_rate_ref

    @api.depends('destination_bank_fee', 'expect_destination_amount')
    def _compute_new_currency_rate_by_expected_cost(self):
        for rec in self:
            if rec.expect_destination_amount > 0 and rec.amount > 0:
                rec.expected_destination_currency_rate = rec.expect_destination_amount * rec.payment_currency_rate / rec.amount

    def write(self, vals):
        for rec in self:
            if rec.payment_type == 'transfer':
                # for payment
                if vals.get('payment_currency_rate') is not None and vals.get('payment_currency_rate') > 0:
                    vals['payment_currency_rate_ref'] = vals.get('payment_currency_rate')
                    currency_id = vals.get('currency_id')
                    if not currency_id:
                        currency_id = rec.currency_id.id
                    self.env['res.currency.rate'].sudo().search([('currency_id', '=', currency_id)],
                                                                limit=1).write({
                        'rate': vals.get('payment_currency_rate')
                    })

                # for sender
                if vals.get('currency_rate') is not None and vals.get('currency_rate') > 0:
                    vals['currency_rate_ref'] = vals.get('currency_rate')
                    if vals.get('journal_id'):
                        currency_id = self.env['account.journal'].browse(vals.get('journal_id')).currency_id
                        if currency_id is None or currency_id.id is False:
                            currency_id = self.env['res.users'].sudo().browse(
                                self._uid).company_id.currency_id.id
                        else:
                            currency_id = currency_id.id
                        self.env['res.currency.rate'].sudo().search([('currency_id', '=', currency_id)],
                                                                    limit=1).write({
                            'rate': vals.get('currency_rate')
                        })
                    else:
                        currency_ids = rec.journal_id[0]['currency_id'].ids
                        if len(currency_ids) > 0:
                            currency_id = currency_ids[0]
                        else:
                            currency_id = self.env['res.users'].sudo().browse(
                                self._uid).company_id.currency_id.id
                        self.env['res.currency.rate'].sudo().search(
                            [('currency_id', '=', currency_id)],
                            limit=1).write({
                            'rate': vals.get('currency_rate')
                        })
                # for destination
                if vals.get('destination_currency_rate') is not None and vals.get('destination_currency_rate') > 0:
                    vals['destination_currency_rate_ref'] = vals.get('destination_currency_rate')
                    if vals.get('destination_journal_id'):
                        currency_id = self.env['account.journal'].browse(vals.get('destination_journal_id')).currency_id
                        if currency_id is None or currency_id.id is False:
                            currency_id = self.env['res.users'].sudo().browse(
                                self._uid).company_id.currency_id.id
                        else:
                            currency_id = currency_id.id
                        self.env['res.currency.rate'].sudo().search([('currency_id', '=', currency_id)],
                                                                    limit=1).write({
                            'rate': vals.get('destination_currency_rate')
                        })
                    else:
                        currency_ids = self.destination_journal_id[0]['currency_id'].ids
                        if len(currency_ids) > 0:
                            currency_id = currency_ids[0]
                        else:
                            currency_id = self.env['res.users'].sudo().browse(
                                self._uid).company_id.currency_id.id
                        self.env['res.currency.rate'].sudo().search(
                            [('currency_id', '=', currency_id)],
                            limit=1).write({
                            'rate': vals.get('destination_currency_rate')
                        })
        return super(AccountPayment, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('payment_type') == 'transfer' and vals.get('payment_currency_rate'):
            # for payment
            self.env['res.currency.rate'].sudo().search([('currency_id', '=', self.currency_id.id)],
                                                        limit=1).write({
                'rate': vals.get('payment_currency_rate')
            })
            # for sender
            currency_id = self.env['account.journal'].browse(vals.get('journal_id')).currency_id
            if currency_id is None or currency_id.id is False:
                currency_id = self.env['res.users'].sudo().browse(
                    self._uid).company_id.currency_id.id
            else:
                currency_id = currency_id.id
            self.env['res.currency.rate'].sudo().search([('currency_id', '=', currency_id)],
                                                        limit=1).write({
                'rate': vals.get('currency_rate')
            })
            # for destination
            currency_id = self.env['account.journal'].browse(vals.get('destination_journal_id')).currency_id
            if currency_id is None or currency_id.id is False:
                currency_id = self.env['res.users'].sudo().browse(
                    self._uid).company_id.currency_id.id
            else:
                currency_id = currency_id.id
            self.env['res.currency.rate'].sudo().search([('currency_id', '=', currency_id)],
                                                        limit=1).write({
                'rate': vals.get('destination_currency_rate')
            })
            vals['payment_currency_rate_ref'] = vals.get('payment_currency_rate')
            vals['currency_rate_ref'] = vals.get('currency_rate')
            vals['destination_currency_rate_ref'] = vals.get('destination_currency_rate')

        return super(AccountPayment, self).create(vals)

    def post(self):
        result = super(AccountPayment, self).post()
        for rec in self:
            if rec.team_id is not None:
                self.env['account.move.line'].sudo().search([('payment_id', '=', rec.id)]).write({
                    'team_id': rec.team_id.id
                })
            try:
                if rec.destination_bank_fee is not None and rec.destination_bank_fee > 1:
                    # create expense
                    # find employee
                    resource = self.env['resource.resource'].sudo().search([('user_id', '=', self.env.user.id)])
                    employee = self.env['hr.employee'].sudo().search([('resource_id', '=', resource.id)])

                    new_expense = self.env['hr.expense'].create({
                        'name': 'Payment Transfer Fee - ' + rec.name,
                        'employee_id': employee.id,
                        'product_id': self.env.ref('advanced_invoice.product_product_bank_fee').id,
                        'unit_amount': rec.destination_bank_fee,
                        'vendor': self.env.ref('advanced_invoice.res_partner_bank_fee').id,
                        'expense_location': 1,
                        'expense_type': 'common',
                        'current_payment_id': rec.id
                    })
                    rec.write({
                        'current_hr_expense_id': new_expense.id
                    })
            except Exception as ex:
                a = 0
        return result

    # def action_validate_invoice_payment(self):
    # remove existing additional one
    # account_move = self.env['account.move'].search(
    #     [('use_estimate_money_flow', '=', True), ('payment_ref', '=', self.invoice_ids[0].id)])
    # if len(account_move.ids) > 0:
    #     account_move.sudo().unlink()

    # result = super(AccountPayment, self).action_validate_invoice_payment()
    # create new journal entry
    # account_move = self.env['account.move'].search(
    #     [('use_estimate_money_flow', '=', True), ('payment_ref', '=', self.invoice_ids[0].id)])
    # if len(account_move.ids) == 0 and self.invoice_ids[0].residual > 0:
    #     rec = self.invoice_ids[0]
    #     if rec.type == 'in_invoice':
    #         account_move = self.env['account.move'].sudo().create({
    #             'name': rec.number,
    #             'date': date.today(),
    #             'ref': rec.number,
    #             'journal_id': rec.pre_journal_id.id,
    #             'use_estimate_money_flow': True,
    #             'payment_ref': rec.id
    #         })
    #         account_move_line = [{
    #             'partner_id': rec.partner_id.id,
    #             'account_id': rec.pre_journal_id.default_debit_account_id.id,
    #             'debit': 0,
    #             'credit': rec.residual,
    #             'date': rec.date_invoice,
    #             'date_maturity': rec.date_due,
    #             'move_id': account_move.id,
    #             'use_estimate_money_flow': True,
    #             'currency_id': rec.currency_id.id,
    #         }, {
    #             'partner_id': rec.partner_id.id,
    #             'account_id': rec.account_id.id,
    #             'debit': rec.residual,
    #             'credit': 0,
    #             'date': rec.date_invoice,
    #             'date_maturity': rec.date_due,
    #             'move_id': account_move.id,
    #             'use_estimate_money_flow': True,
    #             'currency_id': rec.currency_id.id,
    #         }]
    #         self.env['account.move.line'].sudo().create(account_move_line)
    #
    #     elif rec.type == 'out_invoice':
    #         account_move = self.env['account.move'].sudo().create({
    #             'name': rec.number,
    #             'date': date.today(),
    #             'ref': rec.number,
    #             'journal_id': rec.pre_journal_id.id,
    #             'use_estimate_money_flow': True,
    #             'payment_ref': rec.id
    #         })
    #         account_move_line = [{
    #             'partner_id': rec.partner_id.id,
    #             'account_id': rec.pre_journal_id.default_debit_account_id.id,
    #             'debit': rec.residual,
    #             'credit': 0,
    #             'date': rec.date_invoice,
    #             'date_maturity': rec.date_due,
    #             'move_id': account_move.id,
    #             'use_estimate_money_flow': True,
    #             'currency_id': rec.currency_id.id,
    #         }, {
    #             'partner_id': rec.partner_id.id,
    #             'account_id': rec.account_id.id,
    #             'debit': 0,
    #             'credit': rec.residual,
    #             'date': rec.date_invoice,
    #             'date_maturity': rec.date_due,
    #             'move_id': account_move.id,
    #             'use_estimate_money_flow': True,
    #             'currency_id': rec.currency_id.id,
    #         }]
    #         self.env['account.move.line'].sudo().create(account_move_line)
    # return result
