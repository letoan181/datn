# -*- coding: utf-8 -*-
# from odoo import http
import odoo.http as http
from odoo.http import request
from odoo import models, fields, api
from datetime import date, datetime


class AdvancedNotification(http.Controller):
    @http.route('/recurrent/notify', type='json', auth="user")
    def notify(self):
        event = True
        return {
            'title': 'Reminder',
            'message': 'Rửa tay thường xuyên: khi đến, khi chấm công, trước và sau khi ăn, khi ho, hắt hơi, khi tiếp xúc, khi đi vệ sinh'
        }


class ResUsers(models.Model):
    _inherit = 'res.users'

    last_session = fields.Date()

    @api.model
    def check_last_session(self):
        user = self.env.user
        if user.last_session != datetime.today().date():
            user.sudo().write({
                'last_session': datetime.today().date()
            })
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
            if employee and employee.birthday and employee.birthday.strftime("%m-%d") == datetime.today().date().strftime("%m-%d"):
                return True
        return False
