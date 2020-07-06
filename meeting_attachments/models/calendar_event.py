# -*- coding: utf-8 -*-
from odoo import models, api, fields


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def action_direct_attachment(self):
        """ This opens Meeting's calendar view to open attachments of current applicant
            @return: Dictionary value for created Meeting view
        """
        action = self.env.ref('meeting_attachments.action_direct_attachments')
        domain = [('res_model', '=', 'hr.applicant'), ('res_id', '=', self.res_id)]
        return {
            'name': action.name,
            'type': action.type,
            'view_mode': action.view_mode,
            'res_model': action.res_model,
            "context": {"create": False, "edit": False, "delete": False, "search_default_user_id": 1},
            'domain': domain
        }
