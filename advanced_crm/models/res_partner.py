# -*- coding: utf-8 -*-

from odoo import models, fields, _


class AdvancedResPartner(models.Model):
    _inherit = "res.partner"

    contact_source = fields.Many2one('utm.source', string='Contact Source')
    contact_type = fields.Selection([('shop_owner', 'Shop Owner'),
                                     ('digital_agency', 'Digital Agency'),
                                     ('partner', 'Partners'),
                                     ('other', 'Other')])
