from odoo import fields, models, api
from odoo.exceptions import ValidationError


class TextAnswerDetail (models.TransientModel):
    _name = "text.answer.detail"
    question = fields.Html("Question")
    answer = fields.Text("Answer")
    max_score = fields.Float("Max Score")
    score = fields.Float("Score")
    user_input_line = fields.Many2one('survey.user_input_line')
    question_answer_id = fields.Many2one('question.answer')

    @api.onchange('score')
    def onchange_score(self):
        for rec in self:
            if rec.score > rec.max_score:
                raise ValidationError(
                    ('Score cannot be higher than max score!!!'))

    def confirm(self):
        self.user_input_line.answer_score = self.score
        self.question_answer_id.already_marked = True
        self.question_answer_id.text_score = self.score

