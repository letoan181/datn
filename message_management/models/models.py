# -*- coding: utf-8 -*-

from odoo import models, api, fields


class AppMessages(models.Model):
    _inherit = 'mail.message'
    attachment_ids_count = fields.Integer(compute='_get_attachment_ids_count',
                                          string="Number of Attachments Message")
    attachment_ids_count_string = fields.Char(compute='_get_attachment_ids_count_string',
                                              string="Number of Attachments Message")

    project_name = fields.Char(string="Project", compute='_compute_project_name', compute_sudo=True, store=True, default='')

    project_task_name = fields.Char(string="Task", compute='_compute_project_task_name', compute_sudo=True, store=True)

    def action_direct_attachment(self):
        action = self.env.ref('message_management.action_attachment_message')
        return {
            'name': action.name,
            'type': action.type,
            'view_mode': action.view_mode,
            'res_model': action.res_model,
            'domain': [('id', 'in', [e.id for e in self.attachment_ids])],
            'context': '{"create": False, "import": False, "edit": False, "delete": False}'
        }

    def _get_attachment_ids_count(self):
        for rec in self:
            rec.attachment_ids_count = len(rec.attachment_ids.ids)

    def _get_attachment_ids_count_string(self):
        for rec in self:
            rec.attachment_ids_count_string = str(len(rec.attachment_ids.ids)) + ' Attachments'

    def action_window(self):
        action = self.env.ref('message_management.message_seen_project')
        return {
            'name': action.name,
            'type': action.type,
            'view_mode': action.view_mode,
            'res_model': action.res_model,
            'domain': [('model', '=', 'project.task'), '|', ('author_id.user_ids.id', '=', self.env.user.id),
                       ('partner_ids', 'parent_of', self.env.user.partner_id.id)],
            'context': '{"create": False, "import": False, "edit": False, "delete": False}'
        }

    @api.depends('model', 'res_id')
    def _compute_project_task_name(self):
        for rec in self:
            if rec.model != 'project.task':
                rec.project_task_name = False
            else:
                self.env.cr.execute("""select name from project_task where id=%s""", (rec.res_id,))
                project_task = self.env.cr.fetchone()
                if project_task:
                    rec.project_task_name = project_task[0]
                else:
                    rec.project_task_name = False

    @api.depends('model', 'res_id')
    def _compute_project_name(self):
        for rec in self:
            if rec.model != 'project.task':
                rec.project_name = False
            else:
                self.env.cr.execute("""select project_id from project_task where id=%s""", (rec.res_id,))
                project_id = self.env.cr.fetchone()
                self.env.cr.execute("""select name from project_project where id=%s""", (project_id[0],))
                project_name = self.env.cr.fetchone()
                if project_name:
                    rec.project_name = project_name[0]
                else:
                    rec.project_name = False


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def write(self, vals):
        for rec in self:
            print(vals)
            if 'name' in vals:
                rec.env.cr.execute("""update mail_message set project_task_name = %s where res_id=%s""",
                                   (vals['name'], rec.id,))
            super(ProjectTask, rec).write(vals)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def write(self, vals):
        for rec in self:
            if 'name' in vals:
                for e in rec.task_ids:
                    rec.env.cr.execute("""update mail_message set project_name = %s where res_id=%s""",
                                       (vals['name'], e.id,))
            super(ProjectProject, self).write(vals)
