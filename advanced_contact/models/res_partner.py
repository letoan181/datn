from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    unsubscribed = fields.Boolean(string='Unsubscribed', default=False)
    need_new_marketing = fields.Boolean(string='Need New Marketing', default=False, compute='_compute_need_new_marketing', store=True)
    is_public = fields.Boolean(default=False)
    is_magenest_employee = fields.Boolean(default=False, related='user_ids.is_magenest_employee', store=True)

    def write(self, vals):
        for rec in self:
            if "active" in vals:
                if not vals.get("active"):
                    vals['unsubscribed'] = True
                    self.env['mail.followers'].search([('partner_id', '=', rec.id)]).unlink()
        return super(ResPartner, self).write(vals)

    def remove_inactive_partner_cron(self):
        partners = self.env['res.partner'].search([('active', '=', False), ('unsubscribed', '=', False)])
        for partner in partners:
            partner.unsubscribed = True
            self.env['mail.followers'].search([('partner_id', '=', partner.id)]).unlink()

    @api.depends('employee', 'sale_order_ids', 'user_ids', 'invoice_ids', 'opportunity_ids')
    def _compute_need_new_marketing(self):
        for rec in self:
            rec.need_new_marketing = True
            if rec.employee:
                rec.need_new_marketing = False
            elif rec.sale_order_ids and len(rec.sale_order_ids) > 0:
                rec.need_new_marketing = False
            elif rec.invoice_ids and len(rec.invoice_ids) > 0:
                rec.need_new_marketing = False
            elif rec.user_ids and len(rec.user_ids) > 0:
                rec.need_new_marketing = False
            elif rec.opportunity_ids and len(rec.opportunity_ids) > 0:
                rec.need_new_marketing = False

    def cron_check_enable_public(self):

        # cron_check_created_task_enable_public
        # create_uids = self.env['project.task'].read_group([('user_id.active', '=', False)], ['create_uid'], ['create_uid'])
        # for e in create_uids:
        #     if e['create_uid']:
        #         current_partner = self.env['res.partner'].search([('id', '=', e['create_uid'][0])])
        #         if current_partner.user_id and current_partner.user_id.active == False:
        #             if current_partner and len(current_partner.user_ids) == 0:
        #                 current_partner.is_public = True
        # search mail message of project task with non user

        # update inactive user partner is public = True
        inactive_users = self.env['res.users'].search([('active', '=', False)])
        for e in inactive_users:
            e.partner_id.is_public = True
            e.partner_id.active = False

        # search remain partner (no public, no related users)
        non_partners = self.env['res.partner'].search(['|', ('is_public', '=', False), ('user_ids', '=', False)])
        mail_message_of_non_partners = self.env['mail.message'].search([('model', '=', 'project.task'), ('author_id', 'in', [e.id for e in non_partners])])
        non_partners_need_update = []
        for e in mail_message_of_non_partners:
            if e.author_id.name not in non_partners_need_update and not e.author_id.user_ids:
                non_partners_need_update.append(e.author_id.name)
                e.author_id.is_public = True
