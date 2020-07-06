# -*- coding: utf-8 -*-

import re
from datetime import date
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AdvancedCRMLead(models.Model):
    _inherit = "crm.lead"

    project_type = fields.Many2one('crm.project.type', "Project Type")
    lost_reason = fields.Text("Lost reason")
    lead_type = fields.Selection([('shop_owner', 'Shop Owner'),
                                  ('digital_agency', 'Digital Agency'),
                                  ('partner', 'Partners'),
                                  ('other', 'Other')])
    # lead_location = fields.Selection([('international', 'International'),
    #                                   ('domestic', 'Domestic')])
    lead_location = fields.Many2one('crm.lead.location', "Lead Location")
    # status = fields.Selection([('new', 'New'), ('open', 'Open')], default='new', track_visibility='always')
    budget = fields.Monetary(string="Budget Amount", currency_field='company_currency')
    # email_notify = fields.Many2many('crm.notify.email', "Email Notify To")
    # Check lead create auto
    auto_create = fields.Boolean(default=False)
    source_detail = fields.Char(string='Source Details')

    # def get_default_status_id(self):
    #     status = self.env.ref('advanced_crm.new').id
    #     return status

    status_id = fields.Many2one(comodel_name='crm.lead.status', string='Status', track_visibility='always')
    check_reminder_lead_owner = fields.Boolean(default=False)
    document_count = fields.Integer(compute='_document_count')
    note = fields.Text("Note")
    can_read_users = fields.Many2many('res.users', 'crm_lead_can_read_user_rel', string='Other Users Can Read', compute='_compute_can_read_users', store=True)

    @api.depends('message_partner_ids', 'user_id')
    def _compute_can_read_users(self):
        for rec in self:
            user_ids = []
            if rec.user_id.employee_ids:
                for e in rec.user_id.employee_ids[0].can_read_crm_lead_users:
                    if e.id not in user_ids:
                        user_ids.append(e.id)
            for partner in rec.message_partner_ids:
                if partner.user_ids:
                    if partner.user_ids[0].employee_ids:
                        for e in partner.user_ids[0].employee_ids[0].can_read_crm_lead_users:
                            if e.id not in user_ids:
                                user_ids.append(e.id)
            rec.write({
                'can_read_users': [(6, 0, user_ids)]
            })

    # over ride fields user_id to set domain
    @api.model
    def _compute_get_sale_person(self):
        return self.env.ref('advanced_crm.group_user_assigned_lead').users

    sale_persons = fields.Many2many('res.users', string='Salesperson', store=False, default=_compute_get_sale_person)

    def _document_count(self):
        self.ensure_one()
        # compute amount document
        if self.user_has_groups('base.group_system'):
            domain = self.env['document.crm.part'].sudo().search([('document_crm_id', '=', self.id)])
            self.document_count = len(domain)
        else:
            if len(self.document_crm_part) > 0:
                part_ids = [part.id for part in self.document_crm_part]
                self.env.cr.execute(
                    """select res_id from document_permission where res_user_id=%s and model like 'crm' and res_id in %s group by res_id""",
                    (self._uid, tuple(part_ids)))
                can_read_documents = self.env.cr.fetchall()
                self.document_count = len(can_read_documents)
            else:
                self.document_count = 0

    # check_activity_message = fields.Boolean(string='Check activity and message', default=False,
    #                                         compute='check_schedule_message')
    def action_document_crm_part_list(self):
        if self.user_has_groups('base.group_system'):
            domain = [('document_crm_id', '=', self.id)]
        else:
            domain = [('document_crm_id', '=', self.id)]
            self.env.cr.execute(
                """select res_id from document_permission where res_user_id=%s and model like 'crm' group by res_id""",
                (self._uid,))
            can_read_documents = self.env.cr.fetchall()
            domain.append(('id', 'in', [val[0] for val in can_read_documents]))
        action = {"name": self.name, "type": "ir.actions.act_window", "view_mode": "kanban,form",
                  "view_type": "form",
                  "res_model": "document.crm.part",
                  "context": {"create": True, 'default_document_crm_id': self.id}, 'domain': domain}
        return action

    @api.model
    def default_get(self, fields):
        defaults = super(AdvancedCRMLead, self).default_get(fields)
        if 'status_id' not in defaults:
            status = self.env.ref('advanced_crm.new').id
            defaults['status_id'] = status
        return defaults

    # --Dieu kien
    # Lead o trang thai open
    # Has no Activity schedule in the future (check neu khong co activity nao > hien tai)
    # Last Message or Note was at least 20 days ago
    # --Action
    # Mark Lost Lead
    # Lost Reason: No Response

    def _cron_job_auto_mark_lost_after_20_day(self):
        # thang3797
        status_open = self.env.ref('advanced_crm.open')
        all_lead_open = self.env['crm.lead'].sudo().search([('type', '=', 'lead'), ('status_id', '=', status_open.id)])
        if all_lead_open:
            for lead in all_lead_open:
                check_condition_activity = True
                check_condition_message = True
                mail_message_related_ids = self.env['mail.message'].sudo().search(
                    [('res_id', '=', lead.id), ('model', '=', 'crm.lead')], order='create_date DESC')
                if mail_message_related_ids:
                    # for mail_message_related in mail_message_related_ids:
                    #     print("message " + str(mail_message_related.create_date))
                    last_mail_message = mail_message_related_ids[0]
                    days_from_last_message_to_today_obj = datetime.now().date() - last_mail_message.create_date.date()
                    days = days_from_last_message_to_today_obj.days
                    if days < 20:
                        check_condition_message = False
                mail_activity_related_ids = self.env['mail.activity'].sudo().search(
                    [('res_id', '=', lead.id), ('res_model', '=', 'crm.lead')], order='date_deadline DESC')
                if mail_activity_related_ids:
                    # for mail_acivity_related in mail_activity_related_ids:
                    #     print("activity " + str(mail_acivity_related.date_deadline))
                    last_activity_message = mail_activity_related_ids[0]
                    if last_activity_message.date_deadline > date.today():
                        check_condition_activity = False
                if check_condition_activity and check_condition_message:
                    lead.action_set_lost(lost_reason="No Response")

    # --Dieu kien
    # Lead o trang thai open
    # Has no Activity schedule in the future (check neu khong co activity nao > hien tai)
    # Last action done was at least 3 days old (Log Note, Send Message, Activity Completion)
    # --Action
    # Automatically schedule a Reminder Activity for the Lead Owner
    # Deadline = [Today]
    def _cron_job_auto_reminder_after_3_day(self):
        model = self.sudo().env['ir.model'].search([('model', '=', 'crm.lead')])
        status_open = self.env.ref('advanced_crm.open')
        all_lead_open = self.env['crm.lead'].sudo().search(
            [('type', '=', 'lead'), ('status_id', '=', status_open.id), ('check_reminder_lead_owner', '=', False)])
        for lead in all_lead_open:
            check_condition_activity = True
            check_condition_message = True
            check_activity_done = True
            mail_message_related_ids = self.env['mail.message'].sudo().search(
                [('res_id', '=', lead.id), ('model', '=', 'crm.lead')], order='create_date DESC')
            # check xem co messgage hay log note trong 3 ngay gan nhat ko
            if mail_message_related_ids:
                last_mail_message = mail_message_related_ids[0]
                days_from_last_message_to_today_obj = datetime.now().date() - last_mail_message.create_date.date()
                days = days_from_last_message_to_today_obj.days
                if days < 3:
                    check_condition_message = False
            mail_activity_related_ids = self.env['mail.activity'].sudo().search(
                [('res_id', '=', lead.id), ('res_model', '=', 'crm.lead')], order='date_deadline DESC')
            # check xem co activity trong tuong lai hay ko
            if mail_activity_related_ids:
                # for mail_acivity_related in mail_activity_related_ids:
                #     days_activity = datetime.now() - mail_acivity_related.create_date
                #     if days_activity.days <= 3:
                #         check_activity_done = False
                #         break
                last_activity_message = mail_activity_related_ids[0]
                if last_activity_message.date_deadline > date.today() - relativedelta(days=3):
                    check_activity_done = False
                # neu co thi dieu kien bang False
                if last_activity_message.date_deadline > date.today():
                    check_condition_activity = False
            if check_condition_activity and check_condition_message and check_activity_done:
                activity_vals = {
                    'res_id': lead.id,
                    'res_model_id': model.id,
                    'res_model': 'crm.lead',
                    'activity_type_id': self.env.ref('note.mail_activity_data_reminder').id,
                    'user_id': lead.user_id.id if lead.user_id else False,
                    'date_deadline': date.today()

                }
                lead.update({
                    'check_reminder_lead_owner': True,
                })
                self.env['mail.activity'].sudo().create(activity_vals)

    def _cron_job_auto_reminder_opp_after_3_day(self):
        model = self.sudo().env['ir.model'].search([('model', '=', 'crm.lead')])
        status_open = self.env.ref('advanced_crm.open')
        all_opportunity_open = self.env['crm.lead'].sudo().search(
            [('type', '=', 'opportunity'), ('check_reminder_lead_owner', '=', False)])
        for opportunity in all_opportunity_open:
            check_condition_activity = True
            check_condition_message = True
            check_activity_done = True
            mail_message_related_ids = self.env['mail.message'].sudo().search(
                [('res_id', '=', opportunity.id), ('model', '=', 'crm.lead')], order='create_date DESC')
            # check xem co messgage hay log note trong 3 ngay gan nhat ko
            if mail_message_related_ids:
                last_mail_message = mail_message_related_ids[0]
                days_from_last_message_to_today_obj = datetime.now().date() - last_mail_message.create_date.date()
                days = days_from_last_message_to_today_obj.days
                if days < 3:
                    check_condition_message = False
            mail_activity_related_ids = self.env['mail.activity'].sudo().search(
                [('res_id', '=', opportunity.id), ('res_model', '=', 'crm.lead')], order='date_deadline DESC')
            # check xem co activity trong tuong lai hay ko
            if mail_activity_related_ids:
                # for mail_acivity_related in mail_activity_related_ids:
                #     days_activity = datetime.now() - mail_acivity_related.create_date
                #     if days_activity.days <= 3:
                #         check_activity_done = False
                #         break
                last_activity_message = mail_activity_related_ids[0]
                if last_activity_message.date_deadline > date.today() - relativedelta(days=3):
                    check_activity_done = False
                # neu co thi dieu kien bang False
                if last_activity_message.date_deadline > date.today():
                    check_condition_activity = False
            if check_condition_activity and check_condition_message and check_activity_done:
                activity_vals = {
                    'res_id': opportunity.id,
                    'res_model_id': model.id,
                    'res_model': 'crm.lead',
                    'activity_type_id': self.env.ref('note.mail_activity_data_reminder').id,
                    'user_id': opportunity.user_id.id if opportunity.user_id else False,
                    'date_deadline': date.today()
                }
                opportunity.update({
                    'check_reminder_lead_owner': True,
                })
                self.env['mail.activity'].sudo().create(activity_vals)

    # check lead ko co schedule activity, last message, log not it nhat 30 days ago
    # gui email thong bao cho nhung email config tich checkbox
    # def check_schedule_message(self):
    #     all_lead = self.env['crm.lead'].search([('type', '=', 'lead')])
    #     if all_lead:
    #         for lead in all_lead:
    #             mail_message_lead_id = lead.env['mail.message'].sudo().search(
    #                 [('res_id', '=', lead.id)])
    #             mail_activity_lead_id = lead.env['mail.activity'].sudo().search(
    #                 [('res_id', '=', lead.id)])
    #             if mail_message_lead_id:
    #                 last_mail_message = mail_message_lead_id[0]
    #                 days_from_last_message_to_today = datetime.now() - last_mail_message.create_date
    #                 days = days_from_last_message_to_today.days
    #                 if days >= 30:
    #                     self.check_activity_message = True
    #             if mail_activity_lead_id:
    #                 last_activity_message = mail_activity_lead_id[0]
    #                 if last_activity_message.date_deadline < date.today():
    #                     self.check_activity_message = True

    def cron_job_check_activity_message(self):
        all_lead = self.env['crm.lead'].sudo().search([('type', '=', 'opportunity')])
        check_send_email = self.env['crm.notify.email'].sudo().search([('send_email_notification', '=', True)])
        if all_lead:
            for lead in all_lead:
                check_activity_message = False
                check_activity_future = True
                mail_message_lead_id = lead.env['mail.message'].sudo().search(
                    [('res_id', '=', lead.id), ('model', '=', 'crm.lead')], order='create_date DESC')
                mail_activity_lead_id = lead.env['mail.activity'].sudo().search(
                    [('res_id', '=', lead.id), ('res_model', '=', 'crm.lead'), ('date_deadline', '>', date.today())])
                if mail_message_lead_id:
                    last_mail_message = mail_message_lead_id[0]
                    # print(mail_message_lead_id[0].body)
                    days_from_last_message_to_today = datetime.now().date() - last_mail_message.create_date.date()
                    days = days_from_last_message_to_today.days
                    if days > 30:
                        check_activity_message = True
                if len(mail_activity_lead_id) > 0:
                    check_activity_future = False
                if check_activity_message and check_activity_future and len(check_send_email) > 0:
                    Mail = self.env['mail.mail'].sudo()
                    for email in check_send_email:
                        mail = Mail.create({
                            'author_id': self.env.user.partner_id.id,
                            'subject': '[Odoo] Opportunity Alert',
                            'email_to': email.name,
                            'body_html': "Opportunity Name: %s assign to %s no action since 30 days ago" % (
                                lead.name,
                                lead.user_id.name)
                        })
                        if mail:
                            mail.send(auto_commit=False, raise_exception=False)

    def action_set_won(self):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            # Required quotation when mark won
            quotations = self.env['sale.order'].sudo().search([('opportunity_id', '=', lead.id)])
            if len(quotations) == 0:
                raise UserError(_('Can not mark won opportunity when not relate any quotation.'))
            stage_id = lead._stage_find(domain=[('is_won', '=', True)])
            lead.write({'stage_id': stage_id.id, 'probability': 100})
        self._rebuild_pls_frequency_table_threshold()
        return True

    def action_set_lost_apply(self):
        view = self.env.ref('advanced_crm.crm_lead_lost_reason_form')

        return {
            'name': _('Mark As Lost'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.lead.lost.reason',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
        }

    # @api.onchange('lead_location')
    # def onchange_lead_location(self):
    #     if self.type == 'lead':
    #         if 'import_file' in self._context or self.auto_create == True:
    #             self.user_id = self.env['crm.lead.location'].sudo().browse(self.lead_location.id).owner_user

    # @api.onchange('project_type')
    # def onchange_project_type(self):
    #     if self.type == 'lead':
    #         if self.project_type:
    #             body = self.project_type.note
    #             self.message_post(body=body, subject='Qualifying Questions')

    @api.model
    def create(self, value):
        if 'import_file' in self._context:
            value.update({
                'auto_create': True
            })
        if 'lead_location' in value and 'auto_create' in value:
            if value['auto_create'] == True:
                value.update({
                    'user_id': self.env['crm.lead.location'].sudo().browse(value['lead_location']).owner_user.id
                })
        record = super(AdvancedCRMLead, self).create(value)
        # auto log note base on project_type
        if record.project_type:
            body = record.project_type.note
            record.message_post(body=body, subject='Qualifying Questions')
        # send email to sale person
        template_1 = self.env.ref('advanced_contact_form.new_lead_coming_template')
        template_2 = self.env.ref('advanced_crm.new_lead_coming_template_notify_lead_owner')
        if record.user_id:
            email = record.user_id.partner_id.email
            if email:
                try:
                    self.env['mail.template'].sudo().browse(template_2.id) \
                        .send_mail(res_id=record.id, force_send=True,
                                   email_values={
                                       'email_to': email})
                except Exception as ex:
                    a = 0
            # # Notify lead owner
            # post_vars = {'subject': res.name,
            #              'body': "You have been assign to new lead",
            #              'partner_ids': [res.user_id.partner_id.id], }
            # res.message_post(
            #     type="notification",
            #     subtype="mt_comment",
            #     **post_vars)
        # send mail to specify person( lead auto created from web. email, or import)
        if record.auto_create:
            # email = self.env['crm.notify.email'].sudo().browse(value['email_notify']).name
            emails = self.env['crm.notify.email'].sudo().search([('active', '=', True)])
            email_list = set(e.name for e in emails)
            if len(email_list) > 0:
                try:
                    self.env['mail.template'].sudo().browse(template_1.id) \
                        .send_mail(res_id=record.id, force_send=True,
                                   email_values={
                                       'email_to': ','.join(email_list)})
                except Exception as ex:
                    a = 0
        if self.env.context.get('default_type') == 'opportunity':
            if record.stage_id and 'project_type' in value:
                project_type = self.env['crm.project.type'].sudo().search([('id', '=', value['project_type'])])
                if project_type:
                    if project_type.guideline_ids:
                        for guideline in project_type.guideline_ids:
                            if guideline.stage_id.id == record.stage_id.id and guideline.guideline:
                                record.message_post(body=str(guideline.guideline), type='comment')
        # for lead
        else:
            status_lead = self.env.ref('advanced_crm.open')
            if record.status_id:
                if record.status_id.id == status_lead.id:
                    lead_res_model_id = self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1).id
                    activity_lead = {
                        'res_id': record.id,
                        'res_model_id': lead_res_model_id,
                        'activity_type_id': record.env.ref('mail.mail_activity_data_call').id,
                        'date_deadline': datetime.now() + relativedelta(days=1),
                        'user_id': record.user_id.id
                    }
                    self.env['mail.activity'].create(activity_lead)

        return record

    def write(self, value):
        # record = super(AdvancedCRMLead, self).write(value)
        for lead in self:
            # log new Qualifying Questions base on project type if lead is new
            if 'project_type' in value and lead.status_id == self.env.ref('advanced_crm.new'):
                body = self.env['crm.project.type'].sudo().browse(value['project_type']).note
                if body:
                    lead.message_post(body=body, subject='Qualifying Questions')
            # Check has document when change stage.
            # if 'stage_id' in value and self.env['crm.stage'].sudo().browse(value['stage_id']).name in ['Pitch', 'Proposal', 'Negotiate', 'Won']:
            #     if lead.type == 'opportunity':
            #         doc = 0
            #         if lead.document_crm_part:
            #             for part in lead.document_crm_part:
            #                 crm_files = self.env['document.crm.file'].sudo().search([('res_id', '=', part.id)])
            #                 doc += len(crm_files)
            #         if doc == 0:
            #             raise UserError(_('Required Document File For This Opportunity BeFore Change Stage'))
            error = ''
            # required project type, lead type when covert lead to opp
            if lead.type == 'lead' and 'type' in value:
                lead.check_reminder_lead_owner = False
                if not lead.project_type:
                    error += 'Project Type,'
                if not lead.lead_type:
                    error += 'Lead type'
            if error != '':
                raise UserError(_('Convert lead to opportunity required %s on lead.') % error)
            # send email notify when re-assign and lead is new
            if 'user_id' in value and lead.status_id == self.env.ref('advanced_crm.new'):
                template_2 = self.env.ref('advanced_crm.new_lead_coming_template_notify_lead_owner')
                email_sale_person = self.env['res.users'].sudo().browse(value['user_id']).partner_id.email
                if email_sale_person:
                    try:
                        self.env['mail.template'].sudo().browse(template_2.id) \
                            .send_mail(res_id=lead.id, force_send=True,
                                       email_values={
                                           'email_to': email_sale_person})
                    except Exception as ex:
                        a = 0
                # notify to email manager sale
                if lead.auto_create:
                    # email = self.env['crm.notify.email'].sudo().browse(value['email_notify']).name
                    emails = self.env['crm.notify.email'].sudo().search([('active', '=', True)])
                else:
                    emails = []
                if len(emails) > 0:
                    Mail = self.env['mail.mail'].sudo()
                    for email in emails:
                        mail = Mail.create({
                            'author_id': self.env.user.partner_id.id,
                            'subject': '[Odoo] Lead Re-assign',
                            'email_to': email.name,
                            'body_html': "Lead %s re-assign to %s" % (lead.name, self.env['res.users'].sudo().browse(value['user_id']).name)
                        })
                        if mail:
                            mail.send(auto_commit=False, raise_exception=False)
            if lead.type == 'opportunity' and 'stage_id' in value:
                condition_activity_stage = self.env['crm.opportunity.activity'].sudo().search([])
                model = self.sudo().env['ir.model'].sudo().search([('model', '=', 'crm.lead')])
                if condition_activity_stage:
                    for condition in condition_activity_stage:
                        for stage in condition.stage_from_id:
                            if lead.stage_id.id == stage.id:
                                if value['stage_id'] == condition.stage_to_id.id:
                                    activity_vals = {
                                        'res_id': lead.id,
                                        'res_model_id': model.id,
                                        'activity_type_id': condition.activity_type_id.id,
                                        'date_deadline': date.today() + relativedelta(days=condition.day_due),
                                        'user_id': lead.user_id.id if lead.user_id else False,
                                        'summary': condition.summary,
                                        'note': condition.note,
                                    }
                                    self.env['mail.activity'].sudo().create(activity_vals)

                # # Notify lead owner
                # post_vars = {'subject': self.name,
                #              'body': "You have been assign to new lead",
                #              'partner_ids': [self.env['crm.notify.email'].sudo().browse(value['user_id']).partner_id], }
                # self.message_post(
                #     type="notification",
                #     subtype="mt_comment",
                #     **post_vars)
        record = super(AdvancedCRMLead, self).write(value)
        # for opportunity
        for oop in self:
            if oop.type == 'opportunity' or ('type' in value and value['type'] == 'opportunity'):
                change_both_stage_and_project_task = False
                if 'stage_id' in value:
                    if 'project_type' in value:
                        change_both_stage_and_project_task = True
                        project_type = self.env['crm.project.type'].sudo().search([('id', '=', value['project_type'])])
                        if project_type:
                            if project_type.guideline_ids:
                                for guideline in project_type.guideline_ids:
                                    if guideline.stage_id.id == value['stage_id'] and guideline.guideline:
                                        oop.message_post(body=str(guideline.guideline), type='comment')
                    elif oop.project_type:
                        if oop.project_type.guideline_ids:
                            for guideline in oop.project_type.guideline_ids:
                                if guideline.stage_id.id == value['stage_id'] and guideline.guideline:
                                    oop.message_post(body=str(guideline.guideline), type='comment')
                else:
                    if 'project_type' in value:
                        change_both_stage_and_project_task = True
                        project_type = self.env['crm.project.type'].sudo().search([('id', '=', value['project_type'])])
                        if project_type:
                            if project_type.guideline_ids:
                                for guideline in project_type.guideline_ids:
                                    if guideline.stage_id.id == oop.stage_id.id and guideline.guideline:
                                        oop.message_post(body=str(guideline.guideline), type='comment')
                    elif oop.project_type:
                        if oop.project_type.guideline_ids:
                            for guideline in oop.project_type.guideline_ids:
                                if guideline.stage_id.id == oop.stage_id.id and guideline.guideline:
                                    oop.message_post(body=str(guideline.guideline), type='comment')
                if not change_both_stage_and_project_task:
                    if 'project_type' in value:
                        project_type = self.env['crm.project.type'].sudo().search([('id', '=', value['project_type'])])
                        if oop.stage_id:
                            if project_type.guideline_ids:
                                for guideline in project_type.guideline_ids:
                                    if guideline.stage_id.id == oop.stage_id.id and guideline.guideline:
                                        oop.message_post(body=str(guideline.guideline), type='comment')

            if oop.partner_id:
                oop.partner_id.message_subscribe(partner_ids=oop.user_id.partner_id.ids)
                if oop.partner_id.parent_id:
                    oop.partner_id.parent_id.message_subscribe(partner_ids=oop.user_id.partner_id.ids)
                else:
                    pass
        return record

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        # if active crm.lead found with cc or from -> send message
        need_send_message = False
        email_list = []
        active_crm_lead = None
        if 'from' in msg_dict and msg_dict['from'] and len(msg_dict['from']) > 0:
            from_email_search = re.search(r'[\w\.-]+@[\w\.-]+', msg_dict['from'])
            email_list.append(from_email_search.group(0))
        if 'cc' in msg_dict and msg_dict['cc'] and len(msg_dict['cc']) > 0:
            cc_emails = re.findall(r'[\w\.-]+@[\w\.-]+', msg_dict['cc'])
            for e in cc_emails:
                if e not in email_list:
                    email_list.append(e)
        if len(email_list) > 0:
            # active crm.lead have email
            active_crm_lead = self.env['crm.lead'].sudo().search(
                [('active', '=', True), ('email_normalized', 'in', email_list)])
            # check active crm.lead follower partners
            need_check_partner_ids = self.env['res.partner'].sudo().search(
                ['|', ('email', 'in', email_list), ('email_normalized', 'in', email_list)])
            if need_check_partner_ids and len(need_check_partner_ids.ids) > 0:
                active_crm_lead += self.env['crm.lead'].sudo().search(
                    [('active', '=', True), ('message_partner_ids', 'in', need_check_partner_ids.ids)])
            if active_crm_lead and len(active_crm_lead.ids) > 0:
                need_send_message = True
        # else call super
        if need_send_message:
            sent_crm_lead_ids = []
            result = None
            for e in active_crm_lead:
                result = e
                # Todo Fix if many crm.lead.found
                # if e.id not in sent_crm_lead_ids:
                #     sent_crm_lead_ids.append(e.id)
                #     employee_partner_ids = []
                #     for follower in e.message_partner_ids:
                #         if follower.employee:
                #             employee_partner_ids.append(follower.id)
                #     e.sudo().message_post(partner_ids=employee_partner_ids, subtype='mail.mt_comment', message_type='notification')
            return result
        else:
            a = 0
            # update Lead Source: Other
            # Lead Source Details: sales@magenest.com
            # Lead Location: International
            from_str = ''
            subject_str = ''
            if 'from' in msg_dict:
                from_str = msg_dict['from']
            if 'subject' in msg_dict:
                subject_str = msg_dict['subject']
            if custom_values:
                custom_values.update({
                    'source_id': self.env.ref('advanced_crm.advanced_crm_source_other').id,
                    'source_detail': 'From: ' + from_str + ' Subject: ' + subject_str,
                    'lead_location': self.env.ref('advanced_crm.international').id,
                    'auto_create': True,
                })
            else:
                custom_values = {
                    'source_id': self.env.ref('advanced_crm.advanced_crm_source_other').id,
                    'source_detail': 'From: ' + from_str + ' Subject: ' + subject_str,
                    'lead_location': self.env.ref('advanced_crm.international').id,
                    'auto_create': True,
                }
            return super(AdvancedCRMLead, self).message_new(msg_dict, custom_values=custom_values)

    # override to convert contact type and contact source to res.partner
    def convert_opportunity(self, partner_id, user_ids=False, team_id=False):
        customer = False
        if partner_id:
            customer = self.env['res.partner'].browse(partner_id)
        for lead in self:
            if partner_id:
                self.env['res.partner'].sudo().browse(partner_id).write({
                    'contact_source': lead.source_id.id,
                    'contact_type': lead.lead_type
                })
            if not lead.active or lead.probability == 100:
                continue
            vals = lead._convert_opportunity_data(customer, team_id)
            lead.write(vals)

        if user_ids or team_id:
            self.allocate_salesman(user_ids, team_id)

        return True


class CRMLeadLocation(models.Model):
    _name = "crm.lead.location"

    name = fields.Char("Location Name", required=True)
    owner_user = fields.Many2one(
        'res.users', 'Lead Location Owner',
        default=lambda self: self.env.user,
        index=True, required=True)


class CRMLeadProjectType(models.Model):
    _name = "crm.project.type"

    name = fields.Char("Type Name", required=True)
    note = fields.Html('Qualification Questions')
    guideline_ids = fields.Many2many(comodel_name="crm.lead.guideline", string="Guideline for stage")


class CRMLeadNotifyEmail(models.Model):
    _name = "crm.notify.email"

    name = fields.Char("Email", required=True)
    active = fields.Boolean(default=True)
    send_email_notification = fields.Boolean(string="Use to send with no action alert")


class CrmLeadLost(models.TransientModel):
    _name = 'crm.lead.lost.reason'
    _description = 'Get Lost Reason'

    lost_reason = fields.Selection([('not_buy', 'Not in Buying Window'),
                                    ('not_interested', 'Not Interested'),
                                    ('no_response', 'No Response'),
                                    ('low_quality', 'Low Quality'),
                                    ('other', 'Other')], required=True)
    lost_detail = fields.Text("Lost Reason Detail")

    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        if self.lost_reason == 'not_buy':
            reason = 'Not in Buying Window'
        elif self.lost_reason == 'not_interested':
            reason = 'Not Interested'
        elif self.lost_reason == 'no_response':
            reason = 'No Response'
        elif self.lost_reason == 'low_quality':
            reason = 'Low Quality' + '-' + self.lost_detail
        else:
            reason = self.lost_detail
        # leads.sudo().write({
        #     'lost_reason': reason
        # })
        return leads.action_set_lost(lost_reason=reason)


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    @api.model
    def _compute_get_sale_person(self):
        return self.env.ref('advanced_crm.group_user_assigned_lead').users

    sale_persons = fields.Many2many('res.users', string='Salesperson', store=False, default=_compute_get_sale_person)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def message_format(self):
        message_values = super(MailMessage, self).message_format()
        for message in message_values:
            if self.env.user.has_group('advanced_crm.group_user_can_see_revenue_opp'):
                message.update({
                    'tracking_access': 'True'
                })
            else:
                message.update({
                    'tracking_access': 'False'
                })
        return message_values
