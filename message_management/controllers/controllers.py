# -*- coding: utf-8 -*-

# class SeenMessage(http.Controller):
#     @http.route('/seen_message/seen_message/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/seen_message/seen_message/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('seen_message.listing', {
#             'root': '/seen_message/seen_message',
#             'objects': http.request.env['seen_message.seen_message'].search([]),
#         })

#     @http.route('/seen_message/seen_message/objects/<model("seen_message.seen_message"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('seen_message.object', {
#             'object': obj
#         })
