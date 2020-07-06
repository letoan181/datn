from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    can_read_crm_lead_users = fields.Many2many(
        'res.users', 'hr_employee_can_read_crm_lead_user_rel', string="Employees That Can Read His/Her Lead/Oppor")

    def write(self, vals):
        result = super(HrEmployee, self).write(vals)
        if 'can_read_crm_lead_users' in vals:
            # update can read user of this employee crm_lead
            for rec in self:
                if rec.user_id:
                    self.env['crm.lead'].sudo().search([('message_partner_ids', 'in', [rec.user_id.partner_id.id])])._compute_can_read_users()
        return result
