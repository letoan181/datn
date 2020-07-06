from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AdvancedRequestManagement(models.Model):
    _name = 'advanced.request.management'
    _rec_name = 'topic'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def set_employee_default(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)])
        return employee

    topic = fields.Text(string='Topic', required=True, track_visibility='onchange')
    employee = fields.Many2one('hr.employee', string='Employee', default=set_employee_default,
                               track_visibility='onchange', )
    assign_to = fields.Many2one('hr.employee', string="Employee", track_visibility='onchange')
    approve_button_invisible = fields.Boolean(compute='_compute_approve_button_invisible')
    created_by = fields.Char(compute='get_user_create', store=True, track_visibility='onchange')
    priority = fields.Selection([(
        '1', 'Blocker'),
        ('2', 'Critical'),
        ('3', 'Important'),
        ('4', 'Normal'),
        ('5', 'Trivial')], string='Priority', track_visibility='onchange')
    current_status = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('done', 'Done'),
        ('refused', 'Refused')], string='Status', default='draft', track_visibility='onchange')
    cancel_reason = fields.Text(string='Reason', track_visibility='onchange')
    request_detail = fields.One2many('advanced.request.detail', 'request_id', track_visibility='onchange',
                                     ondelete='cascade')
    date_request = fields.Datetime('Date Request', default=datetime.today(), readonly=True)

    def _compute_approve_button_invisible(self):
        for rec in self:
            if rec.current_status == 'to_approve':
                if rec.assign_to.user_id.id == self._uid:
                    rec.approve_button_invisible = True
                else:
                    rec.approve_button_invisible = False
            else:
                rec.approve_button_invisible = False

    def get_user_create(self):
        for e in self:
            login_user = self.env.uid
            e.created_by = login_user

    def submit_request(self):
        self.write({
            'current_status': 'to_approve'
        })

        return

    def approve_button(self):
        submit_person = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        employee_submit = self.assign_to

        if submit_person.id == employee_submit.id:
            detail = self.request_detail
            for e in detail:
                if e.status != 'draft':
                    self.write({
                        'current_status': 'done'
                    })
                else:
                    raise UserError(_('You have finish all requests before approve'))

        else:
            raise UserError(_('You do not have permission to do this action '))

    def refuse_button(self):
        submit_person = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        employee_submit = self.assign_to
        if submit_person.id == employee_submit.id:
            detail = self.request_detail
            for e in detail:
                if e.status != 'draft':
                    self.write({'current_status': 'refused'})
                else:
                    raise UserError(_('You must be refuse all request below'))
        else:
            raise UserError(_('You do not have permission to do this action '))

    def cancel_button(self):
        can_cancel = False
        if self.current_status == 'draft':
            can_cancel = True
        if self.assign_to.user_id.id == self._uid:
            can_cancel = True
        if can_cancel:
            return self.write({
                'current_status': 'draft'
            })
        else:
            raise UserError(_('You do not have permission to do this action '))

    @api.model
    def create(self, vals):
        if 'request_detail' not in vals or len(vals.get('request_detail')) == 0:
            raise UserError(_('You have to fill in request detail'))
        res = super(AdvancedRequestManagement, self).create(vals)
        partner_ids = []
        if len(res.assign_to.ids) > 0:
            partner_ids.append(res.assign_to.user_id.partner_id.id)
        if len(partner_ids) > 0:
            res.message_subscribe(partner_ids=partner_ids)
        return res

    def write(self, vals):
        # check write permission
        can_update = False
        # can update if assigned to or draft
        for rec in self:
            if rec.current_status == 'draft':
                can_update = True
            if rec.current_status != 'done' and rec.current_status != 'refused' and rec.assign_to.user_id.id == self._uid:
                can_update = True
        # old_partner = self.assign_to
        if can_update:
            res = super(AdvancedRequestManagement, self).write(vals)
            if vals.get('request_detail') and len(vals.get('request_detail')) == 0:
                raise UserError(_('You have to fill in request detail'))
            for rec in self:
                if len(rec.request_detail.ids) == 0:
                    raise UserError(_('You have to fill in request detail'))
                new_partner_ids = rec.assign_to
                partner_ids = []
                # for follower in old_partner:
                #     if follower:
                #         self.message_unsubscribe(partner_ids=old_partner.user_id.partner_id.ids)
                for assigned in new_partner_ids:
                    follower_ids = assigned.user_id.partner_id.ids
                    if follower_ids not in partner_ids:
                        partner_ids.append(follower_ids)
                    if follower_ids in partner_ids:
                        rec.message_subscribe(partner_ids=follower_ids)
            return res
        else:
            raise UserError(_('You do not have permission to do this action '))

    def unlink(self):
        for rec in self:
            if not rec.current_status == 'draft':
                raise UserError(_('You have not permission delete'))
        return super(AdvancedRequestManagement, self).unlink()

    def _track_subtype(self, init_values):
        if 'current_status' in init_values:
            self.ensure_one()
            return 'request_management.request_management_notifications'
        return super(AdvancedRequestManagement, self)._track_subtype(init_values)
