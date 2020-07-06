# -*- coding: utf-8 -*-

from odoo import models, api, fields


class InteviewMeeting(models.Model):
    _inherit = 'hr.applicant'

    related_meeting_count = fields.Integer('Interviews', compute='_compute_related_meeting_count')

    def action_make_interview(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        self.ensure_one()
        partners = self.partner_id | self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id
        category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window'].for_xml_id('calendar', 'action_calendar_event')
        res['context'] = {
            'search_default_partner_ids': self.partner_id.name,
            'default_partner_ids': partners.ids,
            'default_user_id': self.env.uid,
            'default_name': self.name,
            'default_categ_ids': category and [category.id] or False,
        }
        res['domain'] = [('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.ids)]
        return res

    def _compute_related_meeting_count(self):
        for rec in self:
            rec.related_meeting_count = len(
                self.env['calendar.event'].sudo().search([('res_model', '=', 'hr.applicant'), ('res_id', '=', rec.id)]))
