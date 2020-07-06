from odoo import fields
from odoo import http
from odoo.http import request
from odoo.tools.misc import formatLang


class AccountMoveLineOnboardingController(http.Controller):

    @http.route('/advanced_invoice/account_move_line_onboarding', auth='user', type='json')
    def account_move_line_onboarding(self):
        company = request.env.user.company_id
        currency = self.currency_id or company.currency_id
        account_sum = 0
        if self.type in ['bank', 'cash']:
            account_ids = tuple(
                ac for ac in [self.default_debit_account_id.id, self.default_credit_account_id.id] if ac)
            if account_ids:
                amount_field = 'aml.balance' if (
                            not self.currency_id or self.currency_id == self.company_id.currency_id) else 'aml.amount_currency'
                query = """SELECT sum(%s) FROM account_move_line aml
                           LEFT JOIN account_move move ON aml.move_id = move.id
                           WHERE aml.account_id in %%s
                           AND move.date <= %%s AND move.state = 'posted';""" % (amount_field,)
                self.env.cr.execute(query, (account_ids, fields.Date.today(),))
                query_results = self.env.cr.dictfetchall()
                if query_results and query_results[0].get('sum') != None:
                    account_sum = query_results[0].get('sum')
        return {
            'html': request.env.ref('advanced_invoice.account_move_line_onboarding_panel').render({
                'current_account_balance': formatLang(self.env, currency.round(account_sum) + 0.0,
                                                      currency_obj=currency),
            })
        }
