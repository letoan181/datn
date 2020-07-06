# -*- coding: utf-8 -*-
from odoo import http


class TestcaseManagement(http.Controller):
    @http.route('/testcase_management/testcase_management/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/testcase_management/testcase_management/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('testcase_management.listing', {
            'root': '/testcase_management/testcase_management',
            'objects': http.request.env['testcase_management.testcase_management'].search([]),
        })

    @http.route(
        '/testcase_management/testcase_management/objects/<model("testcase_management.testcase_management"):obj>/',
        auth='public')
    def object(self, obj, **kw):
        return http.request.render('testcase_management.object', {
            'object': obj
        })
