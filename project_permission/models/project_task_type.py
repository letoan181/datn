# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    @api.model
    def create(self, vals):
        stage = super(ProjectTaskType, self).create(vals)
        if self.env.uid == stage.project_ids.user_id.id:
            return stage
        elif self.user_has_groups('project.group_project_manager'):
            return stage
        else:
            raise UserError("You don't have permission to create new stage!")

    def write(self, vals):
        for rec in self:
            for pr in rec.project_ids:
                if rec.env.uid == pr.user_id.id:
                    a = 0
                elif rec.user_has_groups('project.group_project_manager'):
                    a = 0
                else:
                    raise UserError("You don't have permission to edit stage!")
        return super(ProjectTaskType, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.env.uid == rec.project_ids.user_id.id:
                a = 0
            elif rec.user_has_groups('project.group_project_manager'):
                a = 0
            else:
                raise UserError("You don't have permission to delete stage!")
        return super(ProjectTaskType, self).unlink()
