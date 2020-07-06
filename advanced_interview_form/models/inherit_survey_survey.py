from odoo import models, fields, api


class InheritSurveyQuestion(models.Model):
    _inherit = 'survey.survey'
    maximum_score = fields.Float('Maximum score', compute="compute_maximum_score", readonly=True)

    def compute_maximum_score(self):
        self.env.cr.execute('''SELECT sum(quizz_mark) FROM survey_label WHERE question_id 
                                       IN (SELECT id FROM survey_question WHERE page_id 
                                       IN (SELECT id FROM survey_page WHERE survey_id = %s))''',
                            (self.id,))
        maximum_score = self.env.cr.fetchall()
        self.maximum_score = maximum_score[0][0]
