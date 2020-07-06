from odoo import fields, models, api


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    value_suggested_label = fields.Html(related='value_suggested.value', string="Answer")
    question_answer_id = fields.Many2one('question.answer')


