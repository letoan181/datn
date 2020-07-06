# -*- coding: utf-8 -*-

from odoo import models, fields


class HideProduct(models.Model):
    _inherit = "product.template"
    is_hidden_product = fields.Boolean(string="Hide Product On Sale Order")


# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#     product_id = fields.Many2one('product.product', string='Product',
#                                  domain=[('sale_ok', '=', True), ('hidden_product', '=', False)],
#                                  change_default=True, ondelete='restrict')
