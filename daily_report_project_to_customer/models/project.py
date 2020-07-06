from odoo import models, fields, api, _, tools


class Project(models.Model):
    _inherit = "project.project"

    send_daily_report_to_customer = fields.Boolean(string=_("Send daily report to Customer"), default=False)
    timesheets = fields.One2many('account.analytic.line', 'project_id', string=_("TimeSheets Project"))

    @api.model
    def send_email_customer(self):
        project = self.env['project.project'].sudo().search([('partner_id', '!=', False)])
        template = self.env.ref('report_project.send_daily_report_to_customer_1')
        for partner_id in project:
            if partner_id.send_daily_report_to_customer:
                self.env['mail.template'].sudo().browse(template.id).send_mail(partner_id.id, force_send=True)
