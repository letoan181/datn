# -*- coding: utf-8 -*-
# from odoo import http


# class AdvancedHelpdesk(http.Controller):
#     @http.route('/advanced_helpdesk/advanced_helpdesk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/advanced_helpdesk/advanced_helpdesk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('advanced_helpdesk.listing', {
#             'root': '/advanced_helpdesk/advanced_helpdesk',
#             'objects': http.request.env['advanced_helpdesk.advanced_helpdesk'].search([]),
#         })

#     @http.route('/advanced_helpdesk/advanced_helpdesk/objects/<model("advanced_helpdesk.advanced_helpdesk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('advanced_helpdesk.object', {
#             'object': obj
#         })
