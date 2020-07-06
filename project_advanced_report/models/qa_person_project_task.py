from datetime import datetime, timedelta

from odoo import models, api, fields


class QAPerson(models.Model):
    _inherit = 'project.task'
    qa_deadline = fields.Integer(string='QA Deadline')
    qa_person = fields.Many2one('res.users', string='QA Person', store=True)
    planned_days = fields.Integer(string='Planned Days', compute='compute_planned_days', store=True)

    @api.model
    def default_get(self, fields):
        rec = super(QAPerson, self).default_get(fields)
        context = dict(self._context or {})
        if context.get('default_project_id'):
            project = self.env['project.project'].browse(context['default_project_id'])
            if len(project.ids) > 0:
                rec['qa_person'] = project.user_id.id
        return rec

    @api.onchange('qa_deadline')
    def onchange_qa_deadline(self):
        if self.qa_deadline:
            if self.qa_deadline < 0:
                self.qa_deadline = 0
            else:
                self.qa_deadline = 7

    # def write(self, vals):
    #     for rec in self:
    #         if 'stage_id' in vals:
    #             stage = self.env['project.task.type'].search([('id', '=', vals['stage_id'])])
    #             if stage.name == 'QA' and rec.qa_person.id:
    #                 rec.activity_schedule('project_advanced_report.mail_act_schedule_qa',
    #                                       date_deadline=datetime.today() + timedelta(rec.qa_deadline),
    #                                       user_id=rec.qa_person.id)
    #     return super(QAPerson, self).write(vals)

    @api.depends('date_deadline', 'predict_date_start')
    def compute_planned_days(self):
        for rec in self:
            rec.planned_days = 0
            if rec.date_deadline and rec.predict_date_start:
                rec.planned_days = (rec.date_deadline - rec.predict_date_start).days + 1
