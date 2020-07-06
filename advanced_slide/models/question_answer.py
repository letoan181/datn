from odoo import fields, models, api


class QuestionAnswer (models.Model):
    _name = 'question.answer'
    _description = 'Description'

    name = fields.Char()
    survey_input_id = fields.Many2one(comodel_name='survey.user_input', string='survey_input_id', required=False,  ondelete="cascade")
    question_id = fields.Many2one(comodel_name='survey.question', string='Question', required=False)
    text_score = fields.Float(string='Score', required=False)
    is_correct = fields.Boolean(string='Correct', required=False, compute='compute_is_correct',store=True)
    labels_ids = fields.One2many(
        'survey.label',  related='question_id.labels_ids', string='Default Answer')
    question_title = fields.Html('Question', related='question_id.title')
    user_input_line_ids = fields.One2many(
        'survey.user_input_line', 'question_answer_id', string="Participation's Answer")
    question_type = fields.Selection('Question', related='question_id.question_type')
    already_marked = fields.Boolean(string='Already Marked', default=False)
    state = fields.Selection([
        ('none', 'no need to mark'),
        ('not_marked', 'need to mark'),
        ('marked', 'marked')],  default='none', compute='compute_state', store=True)

    @api.depends('question_type', 'already_marked')
    def compute_state(self):
        for rec in self:
            rec.state = 'none'
            if rec.question_type == 'free_text' and rec.already_marked == True:
                rec.state = 'marked'
            if rec.question_type == 'free_text' and rec.already_marked == False:
                rec.state = 'not_marked'

    @api.depends('labels_ids', 'user_input_line_ids.answer_score')
    def compute_is_correct(self):
        for rec in self:
            rec.is_correct = False
            if rec.question_type == 'free_text':
                rec.is_correct = False
            else:
                max_score = sum(label.answer_score for label in rec.labels_ids)
                score = sum(uil.answer_score for uil in rec.user_input_line_ids)
                if max_score == score:
                    rec.is_correct = True
                for line in rec.user_input_line_ids:
                    if line.answer_score == 0:
                        rec.is_correct = False
                        break

    def view_text_answer(self):
        for rec in self:
            text_answer = rec.user_input_line_ids[0]
            text_max_score = rec.question_id.text_score
            text_score = text_answer.answer_score
            view_id = self.env.ref('advanced_slide.text_answer_detail_form').id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Answer',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'text.answer.detail',
                'target': 'new',
                'context': {
                    'default_question': rec.question_title,
                    'default_answer': text_answer.value_free_text,
                    'default_max_score': text_max_score,
                    'default_score': text_score,
                    'default_user_input_line': text_answer.id,
                    'default_question_answer_id': self.id,
                }
            }


