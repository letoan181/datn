# -*- coding: utf-8 -*-
# Part of Pactera. See LICENSE file for full copyright and licensing details.
import base64
import csv
import io

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from xml.etree import ElementTree as ET
import base64
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for


class SlideQuestionImport(models.TransientModel):
    _name = 'slide.question.import'

    import_file = fields.Binary(string='Import File')
    file_name = fields.Char(string="File Name")

    def confirm_import_question(self):
        import_file_data = base64.b64decode(self.import_file)
        xmlroot = ET.fromstring(import_file_data)
        active_id = self.env.context.get('active_id')
        # label_question = ['', 'A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.', 'H.']
        for multichoiceset in xmlroot.findall('question'):
            if multichoiceset.find('questiontext/text') is not None:
                name = multichoiceset.find('questiontext/text')
                scores = []
                i = 0
                n = 0
                for a in multichoiceset.findall('answer'):
                    point = float(a.get('fraction'))
                    if point > 0:
                        point = 100
                    scores.append(point)
                    n = scores.count(100) * 100
                labels_ids = []
                a = 0
                for answer in multichoiceset.findall('answer/text'):
                    # a += 1
                    # label = label_question[a] if a < len(label_question) else ''
                    label = answer.text
                    label = label.replace("</pre>", "").replace("<pre>", "").replace("<p>", "").replace("</p>", "")
                    score = scores[i] / n
                    is_correct = True
                    if score == 0:
                        is_correct = False
                    labels_ids.append([0, 0, {'answer_score': score,
                                              'is_correct': is_correct,
                                              'value': label}])
                    i = i + 1
                question_tmp = self.env['survey.survey'].browse(active_id).write({
                    'question_and_page_ids':
                        [(0, 0, {
                            'labels_ids': labels_ids,
                            'title': 'Câu hỏi: ' + name.text,
                            'question_type': 'multiple_choice',
                            'is_page': False,
                            'matrix_subtype': 'simple',
                            'constr_mandatory': False,
                        })]

                })
        # return question_tmp


class SurveyUserInput(models.Model):
    """ Metadata for a set of one user's answers to a particular survey """

    _inherit = "survey.user_input"
    question_answer_ids = fields.One2many(comodel_name='question.answer', inverse_name='survey_input_id',
                                          string='question_answer_ids', required=False,
                                          compute='compute_question_answer_ids',
                                          store=True)
    finish_datetime = fields.Datetime(string='Finish date and time', required=False, compute='compute_finish_datetime')
    duration = fields.Char(String="Duration", compute='compute_duration')

    # def action_set_to_entry(self):
    #     list = self.env['survey.user_input'].browse(self._context['active_ids'])
    #     for rec in list:
    #         if rec.state == 'done':
    #             rec.test_entry = True

    def compute_finish_datetime(self):
        for rec in self:
            rec.finish_datetime = False
            if rec.user_input_line_ids:
                date=[]
                for line in rec.user_input_line_ids:
                    date.append(line.create_date)
                rec.finish_datetime = max(date)

    def compute_duration(self):
        for rec in self:
            rec.duration = ''
            if rec.finish_datetime and rec.start_datetime:
                rec.duration = str(rec.finish_datetime - rec.start_datetime).split(".")[0]

    @api.depends('user_input_line_ids')
    def compute_question_answer_ids(self):
        for rec in self:
            dict = {}
            for line in rec.user_input_line_ids:
                if line.question_id not in dict:
                    dict[line.question_id] = [line]
                else:
                    old_value = dict[line.question_id]
                    old_value.append(line)
                    dict[line.question_id] = old_value
            if rec.question_answer_ids:
                rec.question_answer_ids = [(5, 0, 0)]
            for key in dict:
                rec.sudo().write({
                    'question_answer_ids':
                        [(0, 0, {
                            'question_id': key.id,
                            'survey_input_id': self.id,
                            'user_input_line_ids': [(6, 0, [v.id for v in dict[key]])]
                        })]
                })



    @api.depends('user_input_line_ids.answer_score', 'user_input_line_ids.question_id')
    def _compute_quizz_score(self):
        for user_input in self:
            total_possible_score = sum([
                answer_score if answer_score > 0 else 0
                for answer_score in user_input.question_ids.mapped('labels_ids.answer_score')
            ])
            for text_question in user_input.question_ids:
                if text_question.question_type == 'free_text' or text_question.question_type == 'textbox':
                    total_possible_score += text_question.text_score
            if total_possible_score == 0:
                user_input.quizz_score = 0
            else:
                # for input in user_input.user_input_line_ids:
                scores = []
                for qs in user_input.question_ids:
                    total_score_correct = 0
                    for label in qs.labels_ids:
                        if label.is_correct:
                            # total_score_correct += label.answer_score
                            total_score_correct += 1
                    score_input = sum(self.env['survey.user_input_line'].sudo().search(
                        [('user_input_id', '=', user_input.id), ('survey_id', '=', user_input.survey_id.id),
                         ('question_id', '=', qs.id)]).mapped('answer_score'))
                    score_input_correct = len(self.env['survey.user_input_line'].sudo().search(
                        [('user_input_id', '=', user_input.id), ('survey_id', '=', user_input.survey_id.id),
                         ('question_id', '=', qs.id), ('value_suggested.is_correct', '=', True)]))
                    score_input_incorrect = len(self.env['survey.user_input_line'].sudo().search(
                        [('user_input_id', '=', user_input.id), ('survey_id', '=', user_input.survey_id.id),
                         ('question_id', '=', qs.id), ('value_suggested.is_correct', '=', False)]))
                    if score_input_correct == total_score_correct and score_input_incorrect == 0:
                        scores.append(round(score_input))
                score = (sum(scores) / round(total_possible_score)) * 100
                # score = (sum(user_input.user_input_line_ids.mapped('answer_score')) / total_possible_score) * 100
                user_input.quizz_score = round(score, 2) if score > 0 else 0


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'
    question = fields.Html('Question', related="title")
    title = fields.Html('Title', required=True, translate=True)
    text_score = fields.Float(string='Score', required=False)


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    def is_published_toggle(self):
        self.check_access_rights('write')
        if self.is_published == False:
            self.sudo().write({'is_published': True})
        else:
            self.sudo().write({'is_published': False})

    # sh@dowalker
    def _get_channel_slides_base_domain(self):
        base_domain = ['&', request.website.website_domain()[0], '&', ('channel_id', '=', self.id),
                       ('is_category', '=', False)]
        if not self.can_publish:
            if request.website.is_public_user():
                base_domain.append(('website_published', '=', True))
            else:
                base_domain.append('|')
                base_domain.append(('website_published', '=', True), ('user_id', '=', request.env.user.id))
        return base_domain

    def category_data(self):
        domain = self._get_channel_slides_base_domain()
        if self.channel_type == 'documentation':
            sorting = 'latest'
        else:
            sorting = 'sequence'
        order = request.env['slide.slide']._order_by_strategy[sorting]
        return self._get_categorized_slides(domain, order)


class Slide(models.Model):
    _inherit = 'slide.slide'

    @api.depends('document_id', 'slide_type', 'mime_type')
    def _compute_embed_code(self):
        base_url = request and request.httprequest.url_root or self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        if base_url[-1] == '/':
            base_url = base_url[:-1]
        if 'https' not in base_url and 'http' in base_url:
            base_url = base_url.replace('http', 'https')
        for record in self:
            if record.datas and (not record.document_id or record.slide_type in ['document', 'presentation']):
                slide_url = base_url + url_for('/slides/embed/%s?page=1' % record.id)
                record.embed_code = '<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (
                    slide_url, 315, 420)
            elif record.slide_type == 'video' and record.document_id:
                if not record.mime_type:
                    # embed youtube video
                    record.embed_code = '<iframe src="//www.youtube.com/embed/%s?theme=light" allowFullScreen="true" frameborder="0"></iframe>' % (
                        record.document_id)
                else:
                    # embed google doc video
                    record.embed_code = '<iframe src="//drive.google.com/file/d/%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (
                        record.document_id)
            else:
                record.embed_code = False

    # is pupublished toggle
    def is_published_toggle(self):
        self.check_access_rights('write')
        if self.is_published == False:
            self.write({'is_published': True})
        else:
            self.write({'is_published': False})


class CertificateHistory(models.Model):
    _name = 'certificate.history'
    _order = 'id desc'

    survey_id = fields.Many2one('survey.survey')
    user_id = fields.Many2one('res.users')
    total_pass = fields.Integer()
    total_fail = fields.Integer()
    score = fields.Float()
    status = fields.Char()
    date = fields.Date()


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    @api.model
    def create(self, value):
        res = super(SlideChannelPartner, self).create(value)
        if res.channel_id:
            if res.partner_id not in res.channel_id.message_partner_ids:
                res.channel_id.sudo().message_subscribe(partner_ids=[res.partner_id.id])
        return res

    def unlink(self):
        for rec in self:
            if rec.channel_id:
                if rec.partner_id in rec.channel_id.message_partner_ids:
                    rec.channel_id.sudo().message_unsubscribe(partner_ids=[rec.partner_id.id])
        return super(SlideChannelPartner, self).unlink()


class SurveyLabel(models.Model):
    """ Metadata for a set of one user's answers to a particular survey """
    _inherit = "survey.label"

    value = fields.Html('Suggested value', translate=True, required=True)
    value_html = fields.Html('Suggested value')

    @api.model
    def generate(self):
        label_start_with = ['', 'A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.', 'H.', 'I.', 'K.']
        for rec in self:
            a = 0
            label = None
            for label in rec.question_id.labels_ids:
                a += 1
                if label.id == rec.id:
                    label = label
                    break
            if a < len(label_start_with) - 1 and label and not label.value.startswith(label_start_with[a]):
                return label_start_with[a]
        return ''
