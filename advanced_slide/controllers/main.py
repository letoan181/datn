import json
import logging
import werkzeug

from datetime import datetime
from dateutil.relativedelta import relativedelta
from math import ceil

from odoo import fields, http, _
from odoo.addons.base.models.ir_ui_view import keep_query
from odoo.exceptions import UserError
from odoo.http import request, content_disposition
from odoo.tools import ustr
from odoo.addons.survey.controllers.main import Survey
from odoo.exceptions import AccessError, UserError
from odoo.addons.website_slides.controllers.main import WebsiteSlides
from odoo.osv import expression
from odoo.addons.website_slides_survey.controllers.survey import Survey as Survey_Survey
from odoo.addons.website_slides_survey.controllers.slides import WebsiteSlides as Slide

_logger = logging.getLogger(__name__)


class ExtensionWebsiteSlides(Slide):
    # over-ride
    def _prepare_user_slides_profile(self, user):
        values = super(ExtensionWebsiteSlides, self)._prepare_user_slides_profile(user)
        # get user certificate history
        history = request.env['certificate.history'].sudo().search([('user_id', '=', user.id)], limit=10, order="create_date DESC")
        if len(history) > 0:
            certificates_history = []
            for survey in history:
                certificates_history.append({
                    'survey': survey.survey_id.title,
                    'total_pass': survey.total_pass,
                    'total_fail': survey.total_fail,
                    'score': survey.score,
                    'status': survey.status,
                    'date': survey.date,
                })
            values.update({
                'certificates_history': certificates_history
            })
        return values


class ExtensionSurveySurvey(Survey_Survey):
    # over-ride
    # sh@dowalker
    def _prepare_survey_finished_values(self, survey, answer, token=False):
        result = super(ExtensionSurveySurvey, self)._prepare_survey_finished_values(survey, answer, token)
        if answer.slide_id:
            if request.env.user.partner_id and request.env.user.partner_id not in answer.slide_id.channel_id.partner_ids:
                base_url = answer.slide_id.channel_id.get_base_url()
                website_url = '%s/slides' % (base_url)
                result['channel_url'] = website_url
        # print(result)
        # create history survey
        try:
            self._save_certificate_history(result)
        except Exception as e:
            print(e)
        return result

    def _save_certificate_history(self, data=None):
        a = 0
        value = {
            'survey_id': data['survey'].id,
            'user_id': request.env.user.id,
            'total_pass': json.loads(data['graph_data'])[0]['count'],
            'total_fail': json.loads(data['graph_data'])[2]['count'],
            'score': data['answer'].quizz_score,
            'status': 'Pass' if data['answer'].quizz_passed else 'Fail',
            'date': data['answer'].create_date.date()
        }
        if value:
            request.env['certificate.history'].sudo().create(value)
        return True


class ExtensionSurvey(Survey):
    @http.route('/survey/question/<string:survey_token>/<string:answer_token>', type='http', auth='public', website=True)
    def survey_display_question(self, survey_token, answer_token, page_or_question_id, prev=None, **post):
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if survey_sudo.is_time_limited and not answer_sudo.start_datetime:
            # init start date when user starts filling in the survey
            answer_sudo.write({
                'start_datetime': fields.Datetime.now()
            })
        page_or_question_key = 'question' if survey_sudo.questions_layout == 'page_per_question' else 'page'
        # page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, 0, go_back=False)
        page_or_question_id = request.env['survey.question'].sudo().browse(int(page_or_question_id))
        # Get all answer has value
        answer = []
        for input in answer_sudo.user_input_line_ids:
            if not input.skipped:
                answer.append(input.question_id.id)
        questions = []
        count = 0
        if survey_sudo.questions_selection == 'all':
            all_display_questions = survey_sudo.question_ids
        else:
            all_display_questions = answer_sudo.question_ids
        for q in all_display_questions:
            count += 1
            if count < 10:
                counter = '0' + str(count)
            else:
                counter = count
            if survey_sudo.questions_layout == 'page_per_question':
                if q.id == page_or_question_id.id and q.id not in answer:
                    questions.append([counter, q.id, 'brown', 'white', q.page_id.id])
                elif q.id == page_or_question_id.id and q.id in answer:
                    questions.append([counter, q.id, 'brown', 'blue', q.page_id.id])
                elif q.id in answer:
                    questions.append([counter, q.id, 'cadetblue', 'blue', q.page_id.id])
                else:
                    questions.append([counter, q.id, 'cadetblue', 'white', q.page_id.id])
            if survey_sudo.questions_layout == 'page_per_section':
                if q.page_id.id == page_or_question_id.id and q.id not in answer:
                    questions.append([counter, q.id, 'brown', 'white', q.page_id.id])
                elif q.page_id.id == page_or_question_id.id and q.id in answer:
                    questions.append([counter, q.id, 'brown', 'blue', q.page_id.id])
                elif q.id in answer:
                    questions.append([counter, q.id, 'cadetblue', 'blue', q.page_id.id])
                else:
                    questions.append([counter, q.id, 'cadetblue', 'white', q.page_id.id])
        # level questions = 15
        levels = []
        for i in range(0, len(questions), 15):
            levels.append(questions[i:i + 15])
        data = {
            'survey': survey_sudo,
            page_or_question_key: page_or_question_id,
            'answer': answer_sudo,
            'levels': levels,
        }
        if survey_sudo.questions_layout == 'page_per_question':
            if page_or_question_id.id == answer_sudo.question_ids[len(answer_sudo.question_ids) - 1].id:
                data.update({'last': True})
        if survey_sudo.questions_layout == 'page_per_section':
            if page_or_question_id.id == survey_sudo.page_ids[len(survey_sudo.page_ids) - 1].id:
                data.update({'last': True})
        return request.render('survey.survey', data)

    @http.route()
    def survey_display_page(self, survey_token, answer_token, prev=None, **post):
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

        if survey_sudo.is_time_limited and not answer_sudo.start_datetime:
            # init start date when user starts filling in the survey
            answer_sudo.write({
                'start_datetime': fields.Datetime.now()
            })
        # Shadow@lker
        # Get all answer has value
        answer = []
        for input in answer_sudo.user_input_line_ids:
            if not input.skipped:
                answer.append(input.question_id.id)
        questions = []
        count = 0
        question_or_page = None
        if answer_sudo.state == 'new':
            question_or_page, b = survey_sudo.next_page_or_question(answer_sudo, 0, go_back=False)
        if answer_sudo.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            question_or_page, b = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not question_or_page:
                question_or_page, b = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=True)
        if survey_sudo.questions_selection == 'all':
            all_display_questions = survey_sudo.question_ids
        else:
            all_display_questions = answer_sudo.question_ids
        for q in all_display_questions:
            count += 1
            if count < 10:
                counter = '0' + str(count)
            else:
                counter = count
            if q.id not in answer:
                if survey_sudo.questions_layout == 'page_per_question':
                    if q.id == question_or_page.id:
                        questions.append([counter, q.id, 'brown', 'white', q.page_id.id])
                    else:
                        questions.append([counter, q.id, 'cadetblue', 'white', q.page_id.id])
                if survey_sudo.questions_layout == 'page_per_section':
                    # print(q.page_id.id)
                    # print(question_or_page.id)
                    if q.page_id.id == question_or_page.id:
                        questions.append([counter, q.id, 'brown', 'white', q.page_id.id])
                    else:
                        questions.append([counter, q.id, 'cadetblue', 'white', q.page_id.id])
            else:
                if survey_sudo.questions_layout == 'page_per_question':
                    if q.id == question_or_page.id:
                        questions.append([counter, q.id, 'brown', 'blue', q.page_id.id])
                    else:
                        questions.append([counter, q.id, 'cadetblue', 'blue', q.page_id.id])
                if survey_sudo.questions_layout == 'page_per_section':
                    if q.page_id.id == question_or_page.id:
                        questions.append([counter, q.id, 'brown', 'blue', q.page_id.id])
                    else:
                        questions.append([counter, q.id, 'cadetblue', 'blue', q.page_id.id])
        # level questions = 15
        levels = []
        for i in range(0, len(questions), 15):
            levels.append(questions[i:i + 15])
        page_or_question_key = 'question' if survey_sudo.questions_layout == 'page_per_question' else 'page'
        # Select the right page
        # print(answer_sudo.state)
        if answer_sudo.state == 'new':  # First page
            page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, 0, go_back=False)
            data = {
                'survey': survey_sudo,
                page_or_question_key: page_or_question_id,
                'answer': answer_sudo,
                'levels': levels,
            }
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        elif answer_sudo.state == 'done':  # Display success message
            # save certificate history
            # self._save_certificate_history(self._prepare_survey_finished_values(survey_sudo, answer_sudo))
            return request.render('survey.sfinished', self._prepare_survey_finished_values(survey_sudo, answer_sudo))
        elif answer_sudo.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page_or_question_id:
                page_or_question_id, last = survey_sudo.next_page_or_question(answer_sudo, answer_sudo.last_displayed_page_id.id, go_back=True)
            # for input in answer_sudo.user_input_line_ids:

            data = {
                'survey': survey_sudo,
                page_or_question_key: page_or_question_id,
                'answer': answer_sudo,
                'levels': levels,
            }
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        else:
            return request.render("survey.403", {'survey': survey_sudo})

    @http.route('/survey/waiting_result', type='http', auth='none')
    def survey_waiting_result(self):
        return request.render('advanced_slide.thank_for_submit')
        # return "dfvbdfbfgdb"

    @http.route()
    def survey_submit(self, survey_token, answer_token, **post):
        """ Submit a page from the survey.
        This will take into account the validation errors and store the answers to the questions.
        If the time limit is reached, errors will be skipped, answers wil be ignored and
        survey state will be forced to 'done'

        TDE NOTE: original comment: # AJAX submission of a page -> AJAX / http ?? """
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return {}

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if not answer_sudo.test_entry and not survey_sudo._has_attempts_left(answer_sudo.partner_id, answer_sudo.email, answer_sudo.invite_token):
            # prevent cheating with users creating multiple 'user_input' before their last attempt
            return {}

        if survey_sudo.questions_layout == 'page_per_section':
            page_id = int(post['page_id'])
            questions = request.env['survey.question'].sudo().search([('survey_id', '=', survey_sudo.id), ('page_id', '=', page_id)])
            # we need the intersection of the questions of this page AND the questions prepared for that user_input
            # (because randomized surveys do not use all the questions of every page)
            questions = questions & answer_sudo.question_ids
            page_or_question_id = page_id
        elif survey_sudo.questions_layout == 'page_per_question':
            question_id = int(post['question_id'])
            questions = request.env['survey.question'].sudo().browse(question_id)
            page_or_question_id = question_id
        else:
            questions = survey_sudo.question_ids
            questions = questions & answer_sudo.question_ids

        errors = {}
        # Answer validation
        if not answer_sudo.is_time_limit_reached:
            for question in questions:
                answer_tag = "%s_%s" % (survey_sudo.id, question.id)
                errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            if not answer_sudo.is_time_limit_reached:
                for question in questions:
                    answer_tag = "%s_%s" % (survey_sudo.id, question.id)
                    request.env['survey.user_input_line'].sudo().save_lines(answer_sudo.id, question, post, answer_tag)

            vals = {}
            if answer_sudo.is_time_limit_reached or survey_sudo.questions_layout == 'one_page':
                go_back = False
                answer_sudo._mark_done()
            elif 'button_submit' in post:
                go_back = post['button_submit'] == 'previous'
                next_page, last = request.env['survey.survey'].next_page_or_question(answer_sudo, page_or_question_id, go_back=go_back)
                vals = {'last_displayed_page_id': page_or_question_id}

                if next_page is None and not go_back:
                    answer_sudo._mark_done()
                else:
                    vals.update({'state': 'skip'})

            if 'breadcrumb_redirect' in post:
                ret['redirect'] = post['breadcrumb_redirect']
            # sh@dowwalker
            elif 'question_page_redirect' in post:
                ret['redirect'] = post['question_page_redirect']
            else:
                if vals:
                    answer_sudo.write(vals)

                ret['redirect'] = '/survey/fill/%s/%s' % (survey_sudo.access_token, answer_token)
                if go_back:
                    ret['redirect'] += '?prev=prev'
            if 'button_submit' in post:
                if post['button_submit'] == 'finish':
                    if answer_sudo.question_ids:
                        for question in answer_sudo.question_ids:
                            if question.question_type == 'free_text':
                                ret['redirect'] = '/survey/waiting_result'
                                break
        return json.dumps(ret)

    # Survey direct link to a specific page override
    @http.route()
    def survey_change_page(self, survey_token, answer_token, page_id, **post):
        # Controls if the survey can be displayed
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        # show question preview
        answer = []
        for input in answer_sudo.user_input_line_ids:
            if not input.skipped:
                answer.append(input.question_id.id)
        questions = []
        count = 0
        if survey_sudo.questions_selection == 'all':
            all_display_questions = survey_sudo.question_ids
        else:
            all_display_questions = answer_sudo.question_ids
        for q in all_display_questions:
            count += 1
            if count < 10:
                counter = '0' + str(count)
            else:
                counter = count
            if survey_sudo.questions_layout == 'page_per_section':
                if q.page_id.id == request.env['survey.question'].sudo().browse(page_id).id and q.id not in answer:
                    questions.append([counter, q.id, 'brown', 'white', q.page_id.id])
                elif q.page_id.id == request.env['survey.question'].sudo().browse(page_id).id and q.id in answer:
                    questions.append([counter, q.id, 'brown', 'blue', q.page_id.id])
                elif q.id in answer:
                    questions.append([counter, q.id, 'cadetblue', 'blue', q.page_id.id])
                else:
                    questions.append([counter, q.id, 'cadetblue', 'white', q.page_id.id])
        # level questions = 15
        levels = []
        for i in range(0, len(questions), 15):
            levels.append(questions[i:i + 15])
        return request.render('survey.survey', {
            'survey': survey_sudo,
            'page': request.env['survey.question'].sudo().browse(page_id),
            'answer': answer_sudo,
            'levels': levels,
        })


class AdvancedSlide(WebsiteSlides):

    @http.route('/slides-list', type='http', auth="public", website=True)
    def all_channel_list(self, **kw):
        values = self._prepare_user_values(**kw)
        domain = request.website.website_domain()
        channels_all = request.env['slide.channel'].search(domain)
        if not request.env.user._is_public():
            channels_my = channels_all.filtered(lambda channel: channel.is_member).sorted('completion', reverse=True)
            user = request.env.user
        else:
            channels_my = request.env['slide.channel']
            user = False
        channels_popular = channels_all.sorted('total_votes', reverse=True)[:3]
        channels_newest = channels_all.sorted('create_date', reverse=True)[:3]
        values.update({
            'channels_my': channels_my,
            'user': user})
        achievements = request.env['gamification.badge.user'].sudo().search([('badge_id.is_published', '=', True)], limit=5)
        if request.env.user._is_public():
            challenges = None
            challenges_done = None
        else:
            challenges = request.env['gamification.challenge'].sudo().search([
                ('category', '=', 'slides'),
                ('reward_id.is_published', '=', True)
            ], order='id asc', limit=3)
            challenges_done = request.env['gamification.badge.user'].sudo().search([
                ('challenge_id', 'in', challenges.ids),
                ('user_id', '=', request.env.user.id),
                ('badge_id.is_published', '=', True)
            ]).mapped('challenge_id')

        users = request.env['res.users'].sudo().search([
            ('karma', '>', 0),
            ('website_published', '=', True)], limit=5, order='karma desc')
        values.update({
            'channels_popular': channels_popular,
            'channels_newest': channels_newest,
            'achievements': achievements,
            'users': users,
            'top3_users': self._get_top3_users(),
            'challenges': challenges,
            'challenges_done': challenges_done,
        })
        return request.render('advanced_slide.courses_home_list', values)

    @http.route()
    def slides_embed(self, slide_id, page="1", **kw):
        # Note : don't use the 'model' in the route (use 'slide_id'), otherwise if public cannot access the embedded
        # slide, the error will be the website.403 page instead of the one of the website_slides.embed_slide.
        # Do not forget the rendering here will be displayed in the embedded iframe

        # determine if it is embedded from external web page
        referrer_url = request.httprequest.headers.get('Referer', '')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        is_embedded = referrer_url and not bool(base_url in referrer_url) or False
        # try accessing slide, and display to corresponding template
        try:
            slide = request.env['slide.slide'].browse(slide_id)
            if is_embedded:
                request.env['slide.embed'].sudo()._add_embed_url(slide.id, referrer_url)
            values = self._get_slide_detail(slide)
            values['page'] = page
            # remove embed from iframe
            # Sh@dowalker
            if 'https' in base_url:
                values['is_embedded'] = False
            else:
                values['is_embedded'] = is_embedded
            self._set_viewed_slide(slide)
            return request.render('website_slides.embed_slide', values)
        except AccessError:  # TODO : please, make it clean one day, or find another secure way to detect
            # if the slide can be embedded, and properly display the error message.
            return request.render('website_slides.embed_slide_forbidden', {})

    # Over-ride
    def _get_slide_detail(self, slide):
        base_domain = self._get_channel_slides_base_domain(slide.channel_id)
        if slide.channel_id.channel_type == 'documentation':
            related_domain = expression.AND([base_domain, [('category_id', '=', slide.category_id.id)]])

            most_viewed_slides = request.env['slide.slide'].search(base_domain, limit=self._slides_per_aside, order='total_views desc')
            related_slides = request.env['slide.slide'].search(related_domain, limit=self._slides_per_aside)
            category_data = []
            uncategorized_slides = request.env['slide.slide']
        else:
            most_viewed_slides, related_slides = request.env['slide.slide'], request.env['slide.slide']
            category_data = slide.channel_id._get_categorized_slides(
                base_domain, order=request.env['slide.slide']._order_by_strategy['sequence'],
                force_void=True)
            # temporarily kept for fullscreen, to remove asap
            uncategorized_domain = expression.AND([base_domain, [('channel_id', '=', slide.channel_id.id), ('category_id', '=', False)]])
            uncategorized_slides = request.env['slide.slide'].search(uncategorized_domain)
        # sh@dowalker
        if slide.channel_id.nbr_certification > 0:
            channel_slides_ids = slide.channel_id.slide_ids.ids
        else:
            channel_slides_ids = slide.channel_id.slide_content_ids.ids
        slide_index = channel_slides_ids.index(slide.id)
        previous_slide = slide.channel_id.slide_ids[slide_index - 1] if slide_index > 0 else None
        next_slide = slide.channel_id.slide_ids[slide_index + 1] if slide_index < len(channel_slides_ids) - 1 else None

        values = {
            # slide
            'slide': slide,
            'main_object': slide,
            'most_viewed_slides': most_viewed_slides,
            'related_slides': related_slides,
            'previous_slide': previous_slide,
            'next_slide': next_slide,
            'uncategorized_slides': uncategorized_slides,
            'category_data': category_data,
            # user
            'user': request.env.user,
            'is_public_user': request.website.is_public_user(),
            # rating and comments
            'comments': slide.website_message_ids or [],
        }

        # allow rating and comments
        if slide.channel_id.allow_comment:
            values.update({
                'message_post_pid': request.env.user.partner_id.id,
            })

        return values
