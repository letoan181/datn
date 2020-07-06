from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'
    tags_ids = fields.Many2many('project.tags', 'project_tags_project_project_rel', 'project_id', 'tags_id',
                                string="Default Tags for Task")


class Task(models.Model):
    _inherit = 'project.task'

    @api.model
    def default_get(self, fields):
        rec = super(Task, self).default_get(fields)
        context = dict(self._context or {})
        if context.get('default_project_id'):
            project = self.env['project.project'].browse(context['default_project_id'])
            if len(project.ids) > 0:
                rec['tag_ids'] = [(6, 0, project.tags_ids.ids)]
        return rec
