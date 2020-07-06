# -*- coding: utf-8 -*-

from odoo import models, api, fields


class AddFollowers(models.Model):
    _inherit = 'project.project'

    can_edit = fields.Boolean(compute='can_edit_func')

    def can_edit_func(self):
        if self.user_has_groups('project.group_project_manager') or self.env.uid == self.user_id.id:
            self.can_edit = True

    def add_project_follower(self):
        return {
            'name': 'Add Followers',
            'type': "ir.actions.act_window",
            'view_mode': 'form,tree',
            'res_model': 'project.add.follower',
            'context': {'default_project_id': self.id, 'create': True},
            'target': 'new',
        }


class ProjectAddFollower(models.TransientModel):
    _name = 'project.add.follower'

    project_id = fields.Many2one(string='Project', comodel_name='project.project', store=True)
    followers = fields.Many2many('res.partner', string='Followers', store=True)

    def add_followers(self):
        followers_list = []
        for rec in self.followers:
            followers_list.append(rec.id)
        self.sudo().project_id.message_subscribe(followers_list)
        return {'type': 'ir.actions.act_window_close'}


class RemoveFollower(models.Model):
    _inherit = 'project.project'

    def remove_project_follower(self):
        return {
            'name': 'Remove Followers',
            'type': "ir.actions.act_window",
            'view_mode': 'form',
            'res_model': 'project.remove.follower',
            'context': {'default_project_id': self.id},
            'target': 'new',
        }


class ProjectRemoveFollower(models.TransientModel):
    _name = 'project.remove.follower'

    project_id = fields.Many2one(string='Project', comodel_name='project.project')
    followers = fields.Many2many('res.partner', string='Followers', compute='update_list_followers')
    remove_followers_list = fields.Many2many('res.partner')

    @api.depends('project_id')
    def update_list_followers(self):
        for rec in self:
            rec.followers = rec.project_id.message_partner_ids

    def remove_followers(self):
        remove_follower_ids = []
        for rec in self.remove_followers_list:
            remove_follower_ids.append(rec.id)
        self.project_id.sudo().message_unsubscribe(partner_ids=remove_follower_ids)
        return {'type': 'ir.actions.act_window_close'}
