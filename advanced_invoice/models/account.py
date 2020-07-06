# -*- coding: utf-8 -*-

from odoo import models, api, tools, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def action_account_moves_all_statement(self):
        # compute new balance
        account_ids = []
        if self.default_credit_account_id.id:
            account_ids.append(self.default_credit_account_id.id)
        if self.default_debit_account_id.id:
            account_ids.append(self.default_debit_account_id.id)
        current_company_currency_id = self.env.ref('base.main_company').currency_id.id
        for e in account_ids:
            # check current account use amount currency or not
            currency_id = self.env['account.account'].sudo().browse(e).currency_id
            try:
                if currency_id is not None and currency_id.id is not False and currency_id != current_company_currency_id:
                    self.env.cr.execute("""CREATE OR REPLACE FUNCTION update_current_time_balance()
                                      RETURNS VOID AS
                                    $BODY$
                                    DECLARE
                                      r   RECORD;
                                      r_b FLOAT;
                                      a   int;
                                    BEGIN
                                      a = 1;
                                      FOR r IN select id, amount_currency, debit, credit from account_move_line where account_id = %s order by date asc
                                      LOOP
                                        if a = 1
                                        then
                                          r_b = r.amount_currency;
                                          update account_move_line set current_time_balance = r.amount_currency where id = r.id;
                                        end if;
                                        if a > 1
                                        then
                                          r_b = r_b + r.amount_currency;
                                          update account_move_line set current_time_balance = r_b where id = r.id;
                                        end if;
                                        update account_move_line set current_time_balance_sequence = a  where id = r.id;
                                        a = a + 1;
                                      END LOOP;
                                      RETURN;
                                    END
                                    $BODY$
                                    LANGUAGE plpgsql;
                                    SELECT update_current_time_balance();""", (str(e),))
                else:
                    self.env.cr.execute("""CREATE OR REPLACE FUNCTION update_current_time_balance()
                                      RETURNS VOID AS
                                    $BODY$
                                    DECLARE
                                      r   RECORD;
                                      r_b FLOAT;
                                      a   int;
                                    BEGIN
                                      a = 1;
                                      FOR r IN select id, balance, debit, credit from account_move_line where account_id = %s order by date asc
                                      LOOP
                                        if a = 1
                                        then
                                          r_b = r.balance;
                                          update account_move_line set current_time_balance = r.balance where id = r.id;
                                        end if;
                                        if a > 1
                                        then
                                          r_b = r_b + r.balance;
                                          update account_move_line set current_time_balance = r_b where id = r.id;
                                        end if;
                                        update account_move_line set current_time_balance_sequence = a  where id = r.id;
                                        a = a + 1;
                                      END LOOP;
                                      RETURN;
                                    END
                                    $BODY$
                                    LANGUAGE plpgsql;
                                    SELECT update_current_time_balance();""", (str(e),))
            except Exception as ex:
                raise UserError(_('fetch customers %s') % tools.ustr(ex))
        action = self.env.ref('account.action_account_moves_all').read()[0]
        action['domain'] = [('account_id', '=', self.default_debit_account_id.ids[0])]
        action['context'] = {'current_account_id': '1'}
        return action
