# -*- coding: utf-8 -*-

from odoo import models, fields


class CRMLeadStatus(models.Model):
    _name = "crm.lead.status"

    name = fields.Char(string='Name')
