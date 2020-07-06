# -*- coding: utf-8 -*-


from odoo import fields, models, _, tools
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    team_id = fields.Many2one('crm.team', string='Sale Team', store=True)
    current_time_balance = fields.Monetary(string="Current Balance", default=0.0, currency_field='company_currency_id')
    current_time_balance_sequence = fields.Integer(string="Balance Sequence")
    use_estimate_money_flow = fields.Boolean("Use Estimate Money Flow", default=False)
    _order = 'date ASC'

    def action_open_force_update_view(self):
        self.ensure_one()
        views = [(self.env.ref('advanced_invoice.view_move_line_form_force_update').id, 'form')]
        action = {"name": "Force Update Journal", "type": "ir.actions.act_window", "view_mode": "form",
                  "res_model": "account.move.line", "context": {"create": False}, 'view_id': False,
                  'views': views, 'target': 'new', 'flags': {'action_buttons': True}, }

        return action

    # @api.model
    # def default_get(self, fields):
    #     defaults = super(AccountMoveLine, self).default_get(fields)
    #     return defaults

    def _compute_current_time_balances(self):
        account_ids = []
        current_company_currency_id = self.env.ref('base.main_company').currency_id.id
        for e in self:
            if e.account_id.id not in account_ids:
                account_ids.append(e.account_id.id)
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

class AccountMove(models.Model):
    _inherit = 'account.move'

    use_estimate_money_flow = fields.Boolean("Use Estimate Money Flow", default=False)
    payment_ref = fields.Integer("Payment Ref")
