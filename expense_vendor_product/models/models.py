# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ExpenseVendorProduct(models.Model):
    _inherit = "hr.expense"

    vendor = fields.Many2one('res.partner', string=_("Vendor"),  domain="[('supplier_rank', '>', 0)]", required=True)

