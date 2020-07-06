from odoo import _

from odoo import models, fields, api
from odoo.exceptions import UserError


class InheritCalendarEventInterview(models.Model):
    _inherit = "calendar.event"

    survey_id = fields.Many2one('survey.survey', string="Survey")
    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null", oldname="response")
    sum_score_interview = fields.Char('Interview Result', readonly=True, compute='compute_sum_score_interview')

    @api.depends()
    def compute_sum_score_interview(self):
        if self.response_id:
            self.sum_score_interview = 0.0
            self.env.cr.execute('''SELECT sum(quizz_mark) FROM survey_user_input_line WHERE user_input_id = %s ''',
                                (self.response_id.id,))
            total_score_interview = self.env.cr.fetchall()[0][0]
            if self.survey_id is not None:
                self.env.cr.execute('''SELECT sum(quizz_mark) FROM survey_label WHERE question_id 
                                                       IN (SELECT id FROM survey_question WHERE page_id 
                                                       IN (SELECT id FROM survey_page WHERE survey_id = %s))''',
                                    (self.survey_id.id,))
                maximum_score = self.env.cr.fetchall()[0][0]
                self.sum_score_interview = str(total_score_interview) + ' / ' + str(maximum_score)
            else:
                self.sum_score_interview = str(total_score_interview)

    def action_start_interview(self):
        if not self.response_id:
            if self.res_model == 'hr.applicant' and self.res_model_id is not None:
                if not self.applicant_id:
                    if not self.res_id:
                        raise UserError(_("Can't not find survey"))
                    else:
                        applicant = self.env['hr.applicant'].sudo().search([('id', '=', self.res_id)])
                        if len(applicant.ids) > 0:
                            response = self.env['survey.user_input'].sudo().create(
                                {'survey_id': applicant.job_id.survey_id.id})
                            self.response_id = response.id
                            self.survey_id = response.survey_id
                else:
                    response = self.env['survey.user_input'].sudo().create(
                        {'survey_id': self.applicant_id.job_id.survey_id.id})
                    self.response_id = response.id
                    self.survey_id = response.survey_id
            else:
                raise UserError(_("Can't not find survey"))
        else:
            response = self.response_id
        return self.survey_id.with_context(survey_token=response.token).action_start_survey()
