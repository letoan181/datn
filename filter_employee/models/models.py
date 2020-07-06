# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _
from odoo.tools import safe_eval


class FilterDomain(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def action_filter_employee(self):
        user_id = self.env.user.id
        emp = self.env['hr.employee'].search([('user_id', '=', user_id)])
        manager = emp[0].parent_id
        subordinates = emp[0].child_ids
        domain = [
            '|', '|',
            ('id', 'in', [val.id for val in manager]),
            ('id', 'in', [val.id for val in subordinates]),
            ('id', 'in', [val.id for val in manager.child_ids])
        ]
        action = {"name": "Employee", "type": "ir.actions.act_window", "view_mode": "kanban,form",
                  "res_model": "hr.employee", 'domain': domain}
        return action
