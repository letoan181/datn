# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomUnFollowTask(models.TransientModel):
    _name = 'project.task.unfollow.project'

    @api.model
    def get_default_project(self):
        task_id_current = self._context.get('active_id')
        self.env.cr.execute("SELECT project_id FROM project_task WHERE id = %s", (task_id_current,))
        project_id_current = self.env.cr.fetchone()
        return self.env['project.project'].search([('id', '=', project_id_current)])

    project = fields.Many2many("project.project", string="Project", default=get_default_project)

    def un_follow_other_people_task_of_project(self):
        for rec in self:
            project_id = rec.project.ids
            current_user_partner_id = self.env['res.users'].browse(self._uid).partner_id.id
            list_task_id = self.env['project.task'].search(
                [('project_id', 'in', project_id), ('user_id', "!=", self._uid)]).ids
            self.env['mail.followers'].sudo().search([
                ('res_id', 'in', list_task_id),
                ('res_model', '=', 'project.task'),
                ('partner_id', '=', current_user_partner_id)
            ]).unlink()


class CustomFollowTask(models.TransientModel):
    _name = 'project.task.follow.project'

    @api.model
    def get_default_project(self):
        task_id_current = self._context.get('active_id')
        self.env.cr.execute("SELECT project_id FROM project_task WHERE id = %s", (task_id_current,))
        project_id_current = self.env.cr.fetchone()
        return self.env['project.project'].search([('id', '=', project_id_current)])

    project = fields.Many2many("project.project", string="Project", default=get_default_project)

    def follow_other_people_task_of_project(self):
        for rec in self:
            for project in rec.project:
                project.task_ids.message_subscribe(partner_ids=[self.env['res.users'].browse(self._uid).partner_id.id])

