from odoo import models, fields, api, _, tools


class ResUsers(models.Model):
    _inherit = "res.users"

    timesheets = fields.One2many('account.analytic.line', 'user_id', string=_("Timesheets Users"))
    em_manger = fields.Many2one('res.partner', string=_("Employee Manger"))

    def get_email_hr_group(self):
        # send group hr
        group_id = self.env['res.groups'].search([('name', '=', '1. HR')])
        list_email = ""
        if group_id and len(group_id) > 0:
            for g_id in group_id:
                for user_id in g_id.users:
                    list_email += user_id.partner_id.email + ","
        return list_email.rstrip(',')

    def get_email_admin_group(self):
        # send group admin settings
        group_id = self.env['res.groups'].search([('name', '=', 'Settings')])
        list_email = ""
        if group_id and len(group_id) > 0:
            for g_id in group_id:
                if g_id.category_id.name == "Administration":
                    for user_id in g_id.users:
                        list_email += user_id.partner_id.email + ","
        return list_email.rstrip(',')


class Employee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def send_3_month_report(self, record):
        template = self.env.ref('daily_report_project_to_customer.notification_timesheets')
        record.user_id.write({'em_manger': record.parent_id.user_id.partner_id.id})
        # send email
        if record:
            self.env['mail.template'].sudo().browse(template.id).send_mail(record.user_id.id, force_send=True)

