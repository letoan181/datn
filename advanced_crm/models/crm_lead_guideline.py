from odoo import api, fields, models


class CrmLeadGuideline(models.Model):
    _name = "crm.lead.guideline"

    stage_id = fields.Many2one(comodel_name="crm.stage", string="Stage")
    guideline = fields.Html(string="Guideline")
