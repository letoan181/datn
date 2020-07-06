# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models,fields


class Message(models.AbstractModel):
    _inherit = 'mail.thread'

    # def _notify_compute_recipients(self, record, msg_vals):
    #     result = super(Message, self)._notify_compute_recipients(record, msg_vals)
    #     try:
    #         if record._name == 'hr.applicant' and len(result['partners']) > 0:
    #             new_partner_list = []
    #             for e in result['partners']:
    #                 if e['type'] == 'user':
    #                     e['notif'] = 'inbox'
    #                     new_partner_list.append(e)
    #                 elif e['type'] == 'customer':
    #                     # current_res_partner = self.env['res.partner'].sudo().browse(e['id'])
    #                     a = 0
    #             result['partners'] = new_partner_list
    #         elif record._name == 'account.move' and len(result['partners']) > 0:
    #             new_partner_list = []
    #             for e in result['partners']:
    #                 if e['type'] == 'user':
    #                     e['notif'] = 'inbox'
    #                     new_partner_list.append(e)
    #                 elif e['type'] == 'customer':
    #                     # current_res_partner = self.env['res.partner'].sudo().browse(e['id'])
    #                     a = 0
    #             result['partners'] = new_partner_list
    #         elif record._name == 'crm.lead' and len(result['partners']) > 0:
    #             new_partner_list = []
    #             for e in result['partners']:
    #                 if e['type'] == 'user':
    #                     e['notif'] = 'inbox'
    #                     new_partner_list.append(e)
    #                 elif e['type'] == 'customer':
    #                     # current_res_partner = self.env['res.partner'].sudo().browse(e['id'])
    #                     a = 0
    #             result['partners'] = new_partner_list
    #         elif record._name == 'sale.order' and len(result['partners']) > 0:
    #             new_partner_list = []
    #             for e in result['partners']:
    #                 if e['type'] == 'user':
    #                     e['notif'] = 'inbox'
    #                     new_partner_list.append(e)
    #                 elif e['type'] == 'customer':
    #                     # current_res_partner = self.env['res.partner'].sudo().browse(e['id'])
    #                     a = 0
    #             result['partners'] = new_partner_list
    #     except Exception as ex:
    #         e = 0
    #     return result
    def _notify_compute_recipients(self, record, msg_vals):
        result = super(Message, self)._notify_compute_recipients(record, msg_vals)
        try:
            # search model apply outgoing mail
            model = []
            models = self.env['apply.outgoing.mail'].sudo().search([], limit=1)
            if len(models) > 0:
                for a in models.model:
                    model.append(a.model)
            if record._name not in model and len(result['partners']) > 0:
                new_partner_list = []
                for e in result['partners']:
                    e['notif'] = 'inbox'
                    new_partner_list.append(e)
                result['partners'] = new_partner_list
        except Exception as ex:
            e = 0
        return result


class ApplySendOutGoingMail(models.Model):
    _name = 'apply.outgoing.mail'

    name = fields.Char()
    model = fields.Many2many('ir.model',string='Model Apply Outgoing Mail')
