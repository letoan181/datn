# -*- coding: utf-8 -*-

from odoo import models, api, fields


class AdvancedUser(models.Model):
    _inherit = 'res.users'

    work_location = fields.Many2one('company.location', 'Company Location')
    is_magenest_employee = fields.Boolean(default=False)

    def write(self, vals):
        if "active" in vals:
            for rec in self:
                if not vals.get("active"):
                    rec.partner_id.is_public = True
                    vals['is_magenest_employee'] = False
                    rec.partner_id.is_magenest_employee = False
                    self.env['mail.followers'].search([('partner_id', '=', rec.partner_id.id)]).unlink()
        return super(AdvancedUser, self).write(vals)

    def mass_update_employee(self):
        # Find all contact has user is employee
        Contact = self.env['res.partner'].sudo()
        User = self.env['res.users'].sudo()
        # Find Internal user
        self.env.cr.execute(
            """select id from res_users where id > 0""")
        users_fetch = self.env.cr.fetchall()
        list_users = set([user[0] for user in users_fetch])
        users = User.browse(list_users)
        list_partner = set([user.partner_id.id for user in users if user.has_group('base.group_user')])
        # Update contact for user
        partners = Contact.browse(list_partner)
        for contact in partners:
            if not contact.employee:
                contact.write({
                    'employee': True
                })
        return True

    def mass_update_related_contact(self):
        for rec in self.env['res.users'].search([]):
            if rec.partner_id:
                # update related res.partner via sale order
                related_sale_order = self.env['sale.order'].search(['|', ('create_uid', '=', rec.id), ('user_id', '=', rec.id)])
                for related_sale_order_item in related_sale_order:
                    if related_sale_order_item.partner_id:
                        related_sale_order_item.partner_id.message_subscribe(partner_ids=[rec.partner_id.id])

                # update related res.partner via account_move
                related_account_move = self.env['account.move'].search([('type', '=', 'out_invoice'), ('create_uid', '=', rec.id)])
                related_account_move += self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_user_id', '=', rec.id)])
                for related_account_move_item in related_account_move:
                    if related_account_move_item.partner_id:
                        related_account_move_item.partner_id.message_subscribe(partner_ids=[rec.partner_id.id])
                # update related res.partner via crm.lead
                related_crm_lead = self.env['crm.lead'].search([('partner_id', '!=', False), ('create_uid', '=', rec.id)])
                related_crm_lead += self.env['crm.lead'].search([('partner_id', '!=', False), ('create_uid', '=', rec.id), ('active', '=', False)])
                related_crm_lead += self.env['crm.lead'].search([('partner_id', '!=', False), ('user_id', '=', rec.id)])
                related_crm_lead += self.env['crm.lead'].search([('partner_id', '!=', False), ('user_id', '=', rec.id), ('active', '=', False)])
                for related_crm_lead_item in related_crm_lead:
                    if related_crm_lead_item.partner_id:
                        related_crm_lead_item.partner_id.message_subscribe(partner_ids=[rec.partner_id.id])
        return True

    @api.onchange('work_location')
    def _onchange_work_location(self):
        if self.partner_id:
            self.partner_id.write({
                'work_location': self.work_location.id
            })


# class AdvancedContact(models.Model):
#     _inherit = 'res.partner'
#
#     work_location = fields.Many2one('company.location', 'Office Area')
#
#     def write(self, value):
#         # res = super(AdvancedContact, self).write(value)
#         if len(self.user_ids) > 0:
#             for user in self.user_ids:
#                 if user.has_group('base.group_user'):
#                     value.update({'employee': True})
#                 if user.work_location:
#                     value.update({'work_location': user.work_location.id})
#         return super(AdvancedContact, self).write(value)


