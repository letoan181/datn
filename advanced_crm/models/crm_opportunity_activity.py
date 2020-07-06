# -*- coding: utf-8 -*-

from odoo import models, fields


class CRMOpportunityActivity(models.Model):
    _name = 'crm.opportunity.activity'
    _rec_name = 'activity_type_id'

    stage_from_id = fields.Many2many(comodel_name='crm.stage', string='Stage from')
    stage_to_id = fields.Many2one(comodel_name='crm.stage', string='Stage to')
    activity_type_id = fields.Many2one(comodel_name='mail.activity.type', string='Activity')
    day_due = fields.Integer(string='Days due')
    summary = fields.Char(string='Summary')
    note = fields.Html(string='Note')
