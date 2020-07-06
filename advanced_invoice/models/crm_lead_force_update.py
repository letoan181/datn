from odoo import fields, models, api


class CrmLeadUpdateSalePerson(models.TransientModel):
    _name = "crm.lead.update.sale.person"

    def _default_crm_lead(self):
        if self._context.get('active_ids'):
            return self.env['crm.lead'].browse(self._context.get('active_ids'))

    crm_leads = fields.Many2many('crm.lead',
                                 string="Record", required=True, default=_default_crm_lead)
    update_sale_person = fields.Many2one('res.users', string='New Sale Person', index=True,
                                         help='Update New Sale Person', default=lambda self: self.env.user)

    def force_update_crm_lead_sale_person(self):
        self.env.cr.execute("""update crm_lead set user_id=%s where id in %s""",
                            (self.update_sale_person.id, tuple(self.crm_leads.ids),))
        return {'type': 'ir.actions.client', 'tag': 'reload'}
