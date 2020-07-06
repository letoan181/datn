# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request


class AdvancedExpense(models.Model):
    _inherit = "hr.expense"

    current_payment_id = fields.Many2one("account.payment", String=_("###Payment"), readonly=True)


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    pre_journal_id = fields.Many2one('account.journal', string='Payment With', store=True)

    # @api.multi
    # def approve_expense_sheets(self):
    #     for rec in self:
    #         if rec.account_move_id and rec.account_move_id.id:
    #             account_move_id = rec.account_move_id.id
    #             rec.write({
    #                 'account_move_id': False
    #             })
    #             request.env['account.move'].browse(account_move_id).sudo().unlink()
    #         if rec.payment_mode == 'company_account':
    #             account_move = request.env['account.move'].sudo().create({
    #                 'name': self.expense_line_ids.name,
    #                 'date': date.today(),
    #                 'ref': self.expense_line_ids.name,
    #                 'journal_id': self.bank_journal_id.id,
    #                 'amount': self.expense_line_ids.total_amount
    #             })
    #             account_move_line = []
    #             account_move_line.append({
    #                 'account_id': rec.bank_journal_id.default_debit_account_id.id,
    #                 'debit': 0,
    #                 'credit': rec.expense_line_ids.total_amount,
    #                 'date': rec.expense_line_ids.date,
    #                 'move_id': account_move.id,
    #                 'name': rec.expense_line_ids.name
    #             })
    #             account_move_line.append({
    #                 'account_id': rec.expense_line_ids.account_id.id,
    #                 'debit': rec.expense_line_ids.unit_amount,
    #                 'credit': 0,
    #                 'date': rec.expense_line_ids.date,
    #                 'move_id': account_move.id,
    #                 'name':rec.expense_line_ids.name
    #             })
    #             if rec.expense_line_ids.tax_ids != False:
    #                 for e in rec.expense_line_ids.tax_ids:
    #                     account_move_line.append({
    #                         'account_id': e.account_id.id,
    #                         'credit': 0,
    #                         'debit': rec.expense_line_ids.unit_amount* e.amount / 100,
    #                         'date': rec.expense_line_ids.date,
    #                         'move_id': account_move.id,
    #                         'name': rec.expense_line_ids.name
    #                     })
    #             request.env['account.move.line'].sudo().create(account_move_line)
    #             self.account_move_id = account_move.id
    #         elif rec.payment_mode == 'own_account':
    #             account_move = request.env['account.move'].sudo().create({
    #                 'name': self.expense_line_ids.name,
    #                 'date': date.today(),
    #                 'ref': self.expense_line_ids.name,
    #                 'journal_id': self.pre_journal_id.id,
    #                 'amount': self.expense_line_ids.total_amount
    #             })
    #             account_move_line = []
    #             account_move_line.append({
    #                 'account_id': rec.pre_journal_id.default_debit_account_id.id,
    #                 'debit': 0,
    #                 'credit': rec.expense_line_ids.total_amount,
    #                 'date': rec.expense_line_ids.date,
    #                 'move_id': account_move.id,
    #                 'name': rec.expense_line_ids.name
    #             })
    #             account_move_line.append({
    #                 'account_id': rec.expense_line_ids.account_id.id,
    #                 'debit': rec.expense_line_ids.unit_amount,
    #                 'credit': 0,
    #                 'date': rec.expense_line_ids.date,
    #                 'move_id': account_move.id,
    #                 'name': rec.expense_line_ids.name
    #             })
    #             if rec.expense_line_ids.tax_ids != False:
    #                 for e in rec.expense_line_ids.tax_ids:
    #                     account_move_line.append({
    #                         'account_id': e.account_id.id,
    #                         'credit': 0,
    #                         'debit': rec.expense_line_ids.unit_amount * e.amount / 100,
    #                         'date': rec.expense_line_ids.date,
    #                         'move_id': account_move.id,
    #                         'name': rec.expense_line_ids.name
    #                     })
    #             request.env['account.move.line'].sudo().create(account_move_line)
    #             self.account_move_id = account_move.id
    #
    #         super(HrExpenseSheet, self).approve_expense_sheets()

    # def action_sheet_move_create(self):
    #     if self.account_move_id and self.account_move_id.id:
    #         account_move_id = self.account_move_id.id
    #         self.account_move_id = False
    #         request.env['account.move'].browse(account_move_id).sudo().unlink()
    #     super(HrExpenseSheet, self).action_sheet_move_create()


class HrExpenseRefuseWizard(models.TransientModel):
    _inherit = "hr.expense.refuse.wizard"

    def expense_refuse_reason(self):
        self.ensure_one()
        if self.hr_expense_sheet_id:
            for rec in self.hr_expense_sheet_id:
                if rec.account_move_id and rec.account_move_id.id:
                    account_move_id = rec.account_move_id.id
                    rec.write({
                        'account_move_id': False
                    })
                    request.env['account.move'].browse(account_move_id).sudo().unlink()
        return super(HrExpenseRefuseWizard, self).expense_refuse_reason()
