# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError


class TaskStage(models.Model):
    _inherit = 'project.task'

    def write(self, values):
        if values.get('stage_id'):
            v_c_user = self.env['res.users'].search([('project_user_type', 'in', ['vendor', 'customer'])])
            if self.env.uid in [val.id for val in v_c_user]:
                a = 0
            else:
                if self.env.uid == self.manager_id.id:
                    a = 0
                else:
                    if self.env.uid == self.user_id.id:
                        a = 0
                    else:
                        if self.user_has_groups('project.group_project_manager'):
                            a = 0
                        else:
                            if self.user_has_groups('project.group_project_manager'):
                                a = 0
                            else:
                                raise UserError('You have not permission to change task stage!')
        return super(TaskStage, self).write(values)
