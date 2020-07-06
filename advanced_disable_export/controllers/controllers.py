# -*- coding: utf-8 -*-
from odoo import http

# class AdvancedDisableExport(http.Controller):
#     @http.route('/advanced_disable_export/advanced_disable_export/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/advanced_disable_export/advanced_disable_export/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('advanced_disable_export.listing', {
#             'root': '/advanced_disable_export/advanced_disable_export',
#             'objects': http.request.env['advanced_disable_export.advanced_disable_export'].search([]),
#         })

#     @http.route('/advanced_disable_export/advanced_disable_export/objects/<model("advanced_disable_export.advanced_disable_export"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('advanced_disable_export.object', {
#             'object': obj
#         })