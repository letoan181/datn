# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AdvancedDisableAction(models.Model):
    _name = 'advanced.disable.action'

    name = fields.Char(readonly=True)
    model = fields.Many2one('ir.model', string="Apply On Model", required=True)
    type = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export'),
        ('export_all', 'Export All'),
        ('archive', 'Archive & UnArchive'),
    ], default="import", string="Action need remove", required=True)
    group = fields.Many2many('res.groups', string='Group Can Accept Action')

    @api.model
    def get_action_permission(self, user_id=None, model=None, type=None):
        has_permission = False
        if model and type and user_id:
            user = self.env['res.users'].sudo().browse(user_id)
            if user._is_admin():
                has_permission = True
            # find group accept action
            record = self.env['advanced.disable.action'].sudo().search([('name', '=', model), ('type', '=', type)], limit=1)
            if len(record) > 0:
                for group in record.group:
                    if user in group.users:
                        has_permission = True
                        break
        return has_permission

    @api.model
    def create(self, value):
        if 'model' in value:
            value.update({
                'name': self.env['ir.model'].sudo().browse(value['model']).model
            })
        return super(AdvancedDisableAction, self).create(value)

    def write(self, value):
        for rec in self:
            if 'model' in value:
                value.update({
                    'name': self.env['ir.model'].sudo().browse(value['model']).model
                })
        return super(AdvancedDisableAction, self).write(value)
