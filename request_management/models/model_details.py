import datetime

import pytz

from odoo import models, fields, _
from odoo.exceptions import UserError


class AdvancedRequestDetail(models.Model):
    _name = 'advanced.request.detail'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    request_id = fields.Many2one('advanced.request.management', ondelete='cascade', string='Assigned To')
    description = fields.Char('Description', required=True)
    status_history = fields.Text(string='Status History', readonly=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('refuse', 'Refuse')
    ], string="Current status", default='draft', readonly=True)
    cancel_reason = fields.Text('Refused Reason')

    def get_timezone(self):
        user_time_zone = pytz.UTC
        if self.env.user.partner_id.tz:
            user_time_zone = pytz.timezone(self.env.user.partner_id.tz)
        return user_time_zone.zone

    def do_accept(self):
        access_right = False
        user_id = None
        if self.request_id.assign_to.user_id:
            user_id = self.request_id.assign_to.user_id.id
        if user_id is not None and user_id == self._uid:
            access_right = True
        if access_right:
            current_approve = self.env['hr.employee'].search([('user_id', '=', self._uid)])
            date_request = datetime.datetime.now()
            date_format = date_request.astimezone(pytz.timezone(self.get_timezone())).strftime("%b %d %Y %H:%M")
            status = current_approve.name + ' ' + 'approved' + ' ' + 'at' + ' ' + date_format
            self.write({
                'status_history': status,
                'status': 'approve',
                'cancel_reason': False
            })
        else:
            raise UserError(_('You do not have permission to do this action'))

    def do_decline(self):
        access_right = False
        user_id = None
        if self.request_id.assign_to.user_id:
            user_id = self.request_id.assign_to.user_id.id
        if user_id is not None and user_id == self._uid:
            access_right = True
        if access_right:
            current_refuse = self.env['hr.employee'].search([('user_id', '=', self._uid)])
            date_request = datetime.datetime.now()
            date_format = date_request.astimezone(pytz.timezone(self.get_timezone())).strftime("%b %d %Y %H:%M")
            status = current_refuse.name + ' ' + 'refuse' + ' ' + 'at' + ' ' + date_format
            self.write({
                'status_history': status,
                'status': 'refuse',
                'cancel_reason': False
            })
        else:
            raise UserError(_('You do not have permission to do this action'))
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'advanced.refuse.reason',
            'view_id': self.env.ref('request_management.advanced_reason_refuse_all').id,
            'target': 'new',
        }

    def do_refresh(self):
        access_right = False
        user_id = None
        if self.request_id.assign_to.user_id:
            user_id = self.request_id.assign_to.user_id.id
        if user_id is not None and user_id == self._uid:
            access_right = True
        if access_right:
            self.write({
                'status_history': '',
                'status': '',
            })
        else:
            raise UserError(_('You do not have permission to do this action'))
