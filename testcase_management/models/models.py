# -*- coding: utf-8 -*-

import logging
import re

from odoo import models, fields, api


class test_project(models.Model):
    _description = 'Test Project'
    _name = 'testcase_management.project'

    name = fields.Char('Test Project Name', required=True, translate=True)

    note = fields.Text(string='Note')
    project_id = fields.Many2one('project.project', 'Project', track_visibility='onchange')

    # project_id = fields.Many2one('project.project', 'Project', track_visibility='onchange')
    # step_ids = fields.One2many('testcase_management.step', 'testproject_id')
    testcase_ids = fields.One2many('testcase_management.testcase_management', 'testproject_id')

    def get_statistic(self, ids):
        project_id = self.env.context.get('project_id')
        _logger = logging.getLogger(__name__)

        _logger.info('get statistic')

        testcase_name = self.env['testcase_management.project'].search([('project_id', '=', project_id)],
                                                                       order='id desc',
                                                                       limit=1)
        html = ''
        i = 0
        if testcase_name:
            p = testcase_name[0]
            html = "<div> Number of testcase  %s </div> <div> Failed %s </div> <div>Passed %s </div> <div>Fixed %s </div> <div> Untested %s</div> " % (
                p.all_test_count, p.failed_count, p.passed_count, p.fixed_count, p.untested_count)

        return html

    def _compute_test_count(self):
        for task in self:
            task.all_test_count = len(task.testcase_ids)

    all_test_count = fields.Integer(
        'Number of testcase',
        compute='_compute_test_count')

    # failed test
    # def _compute_failed(self):
    #     for task in self:
    #
    #        # sql = "SELECT * FROM testcase_management_testcase_management  WHERE testproject_id = %s AND  state = '2'", [task.id]
    #         self.cr.execute("SELECT * FROM testcase_management_testcase_management  WHERE testproject_id = %s AND  state = '2'", [task.id])
    #
    #         result = self.env.cr.fetchall()
    #         task.failed_count = len(result)
    #
    # failed_count = fields.Integer(
    #     'Failed',
    #     compute='_compute_failed')

    # failed test
    def _compute_failed(self):
        for task in self:
            task.failed_count = self.env['testcase_management.testcase_management'].search_count(
                [('testproject_id', '=', task.id), ('state', '=', '1')])

    failed_count = fields.Integer(
        'Failed',
        compute='_compute_failed')

    # passed test
    def _compute_passed(self):
        for task in self:
            task.passed_count = self.env['testcase_management.testcase_management'].search_count(
                [('testproject_id', '=', task.id), ('state', '=', '0')])

    passed_count = fields.Integer(
        'Passed',
        compute='_compute_passed')

    # Fixed test
    def _compute_fixed(self):
        for task in self:
            task.fixed_count = self.env['testcase_management.testcase_management'].search_count(
                [('testproject_id', '=', task.id), ('state', '=', '3')])

    fixed_count = fields.Integer(
        'Fixed',
        compute='_compute_fixed')

    # untest
    def _compute_untested(self):
        for task in self:
            task.untested_count = self.env['testcase_management.testcase_management'].search_count(
                [('testproject_id', '=', task.id), ('state', '=', '2')])

    untested_count = fields.Integer(
        'Untested',
        compute='_compute_untested')


class testcase_suit(models.Model):
    _description = 'Test Suit'
    _name = 'testcase_management.suit'

    name = fields.Char('Test Suit Name', required=True, translate=True)
    project_id = fields.Many2one('project.project', 'Project')
    test_ids = fields.One2many('testcase_management.testcase_management', 'suit_id')
    note = fields.Text(string='Note')

    def mass_update_emppty_project(self):
        for rec in self.env['testcase_management.suit'].search([]):
            if not rec.project_id:
                current_task = self.env['testcase_management.testcase_management'].search([('suit_id', '=', rec.id), ('project_id', '!=', None)], limit=1)
                if current_task:
                    rec.write({
                        'project_id': current_task.project_id.id
                    })
                else:
                    a = 0

class testcase_img(models.Model):
    _description = 'Test Case Image'
    _name = 'testcase_management.img'

    name = fields.Char('Test Case Image', required=True, translate=True)
    test_id = fields.Many2one('testcase_management.testcase_management', string='Test Case')
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as image for the asset, limited to 1024x1024px.")


class testcase_step(models.Model):
    _description = 'Test Step'
    _name = 'testcase_management.step'

    name = fields.Char('Test Step', required=True, translate=True)
    sortOrder = fields.Integer("Sort Order")
    test_id = fields.Many2one('testcase_management.testcase_management', string='Test Case')
    testproject_id = fields.Many2one('testcase_management.project', string='Test Project')

    test_data = fields.Text(string='Test Data', track_visibility='onchange')
    expected_result = fields.Text(string='Expected Result', track_visibility='onchange')
    actual_result = fields.Text(string='Actual Result', track_visibility='onchange', copy=False)

    image_link = fields.Text(string='Image link', track_visibility='onchange', copy=False)
    note = fields.Text(string='Note', track_visibility='onchange', copy=False)
    dev_note = fields.Text(string='Dev Note', track_visibility='onchange', copy=False)

    project_id = fields.Many2one('project.project', 'Project', track_visibility='onchange')

    # test case name
    def _compute_testcasename(self):
        for task in self:
            if task.test_id:
                y = task.test_id

                # testcase_name = self.env['testcase_management.testcase_management'].search_read(
                #         [('id', '=', task.test_id)], fields=['name'])
                task.testcase_name = y.name

    testcase_name = fields.Char(
        'TestCase',
        compute='_compute_testcasename')

    # test case result
    # test case name
    def _compute_result(self):
        for task in self:
            if task.test_id:
                y = task.test_id
                task.result = y.state
                # testcase_rs = self.env['testcase_management.testcase_management'].search_read(
                #     [('id', '=', task.test_id)], fields=['state'])

    STATE_SELECTION = [
        ('0', 'Passed'),
        ('1', 'Failed'),
        ('2', 'Untested'),
        ('3', 'Fixed')
    ]

    result = fields.Selection(STATE_SELECTION,
                              'result',
                              compute='_compute_result')

    # test
    # @api.model
    # def create(self, values):
    #     step = super(testcase_step, self).create(values)
    #     if 'project_id' not in values:
    #         projectId = self._context.get('active_id')
    #         values['project_id'] = projectId
    #
    #     project_model = step.project_id
    #
    #     # retrieve test project
    #     testProj = self.env['testcase_management.project'].browse(project_model.projectTestId)
    #
    #     if testProj:
    #         for x in testProj:
    #             step.testproject_id = x.id
    #     return step
        # @api.multi

    # def write(self, values):

        # urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', line)
        # x = values

        # tcs = super(testcase_step, self).write(values)


class testcase_management(models.Model):
    _name = 'testcase_management.testcase_management'
    _inherit = ['mail.thread']

    _description = 'Test Case'

    orderno = fields.Char(string="SST", copy=False)

    precondition = fields.Text(string='Pre-condition', track_visibility='onchange', copy=True)

    test_data = fields.Text(string='Test Data', track_visibility='onchange', copy=True)

    expected_result = fields.Text(string='Expected Result', track_visibility='onchange', copy=True)

    actual_result = fields.Text(string='Actual Result', track_visibility='onchange', copy=True)

    test_resource = fields.Binary("Resource", attachment=True,
                                  help="This field holds the resource used as script for the asset.", copy=True)
    # test_script = fields.Text(string='Test Script',track_visibility='onchange')

    note = fields.Text(string='Note', track_visibility='onchange', copy=True)

    CRITICALITY_SELECTION = [
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'Major'),
        ('3', 'Critical'),
        ('4', 'Blocker')
    ]

    criticality = fields.Selection(CRITICALITY_SELECTION, 'Criticality', default='1', copy=True)

    TYPE_SELECTION = [
        ('0', 'Functional'),
        ('1', 'Integration'),
        ('2', 'Performance'),
        ('3', 'Unit')
    ]

    type = fields.Selection(TYPE_SELECTION, 'Type', default='0', copy=True)

    STATE_SELECTION = [
        ('0', 'Passed'),
        ('1', 'Failed'),
        ('2', 'Untested'),
        ('3', 'Need Further Discussion')
    ]

    name = fields.Char('Title', required=True, translate=True, copy=True)

    state = fields.Selection(STATE_SELECTION, 'State', default='2', track_visibility='onchange')
    # should tester update the state
    markAsRetest = fields.Boolean('Mark as re-test', default=False, rquired=True)

    lastUpdatedState = fields.Datetime('Last updated test state')

    # last update state

    DEV_STATE_SELECTION = [
        ('0', 'Fixed'),
        ('1', 'Wont fix'),
        ('2', 'Unfixed'),
        ('3', 'Need further discussion'),
        ('4', 'Can not reproduce')
    ]

    dev_state = fields.Selection(DEV_STATE_SELECTION, 'Dev State', default='2', track_visibility='onchange')

    # should developer mark it as retest

    markAsReFixed = fields.Boolean('Mark as re-fixed', default=False, rquired=True)

    lastDevUpdatedState = fields.Datetime('Last updated dev state')

    approved = fields.Boolean('Approved', default=False, track_visibility='onchange')

    user_id = fields.Many2one('res.users', 'Assigned to', copy=True)

    project_id = fields.Many2one('project.project', 'Project', track_visibility='onchange', copy=True)
    task_id = fields.Many2one('project.task', 'Task', track_visibility='onchange', copy=True)

    suit_id = fields.Many2one('testcase_management.suit', 'Suit', track_visibility='onchange', copy=True)

    # test case name

    def _compute_suitname(self):
        for testcase in self:
            testcase.suitname = ''
            if testcase.suit_id:
                y = testcase.suit_id

                testcase.suitname = y.name

    suitname = fields.Char(
        'Suit Name',
        compute='_compute_suitname', copy=True)

    step_ids = fields.One2many('testcase_management.step', 'test_id', required=False, copy=True)

    def _compute_testStepName(self):

        for testcase in self:
            html = ''
            if testcase.step_ids:
                # testcase.step_ids.sort(key=lambda x: x.sortOrder, reverse=True)
                newlist = sorted(testcase.step_ids, key=lambda x: x.sortOrder, reverse=False)

                for stepObj in newlist:
                    if stepObj.name:
                        html += '<p> ' + stepObj.name + '</p>'

            testcase.stepNames = html

    stepNames = fields.Html(
        'Test Step',
        compute='_compute_testStepName', track_visibility='onchange', copy=True)

    # expectedResult
    def _compute_expectedResult(self):
        for testcase in self:
            html = ''
            if testcase.step_ids:
                # testcase.step_ids.sort(key=lambda x: x.sortOrder, reverse=True)
                newlist = sorted(testcase.step_ids, key=lambda x: x.sortOrder, reverse=False)

                for stepObj in newlist:
                    if stepObj.expected_result:
                        html += '<p> ' + stepObj.expected_result + '</p>'

            testcase.expectedResult = html

    expectedResult = fields.Html(
        'Expected Result',
        compute='_compute_expectedResult', track_visibility='onchange', copy=True)

    # actualResult
    def _compute_actualResult(self):
        for testcase in self:
            html = ''
            if testcase.step_ids:

                # testcase.step_ids.sort(key=lambda x: x.sortOrder, reverse=True)
                newlist = sorted(testcase.step_ids, key=lambda x: x.sortOrder, reverse=False)

                for stepObj in newlist:
                    if stepObj.actual_result:
                        html += '<p> ' + stepObj.actual_result + '</p>'

            testcase.actualResult = html

    actualResult = fields.Html(
        'Actual Result',
        compute='_compute_actualResult', track_visibility='onchange', copy=True)

    # imgLink
    def _compute_imgLink(self):
        for testcase in self:
            html = ''
            if testcase.step_ids:

                newlist = sorted(testcase.step_ids, key=lambda x: x.sortOrder, reverse=False)
                # testcase.step_ids.sort(key=lambda x: x.sortOrder, reverse=True)
                for stepObj in newlist:
                    if stepObj.image_link:
                        regex = r'('

                        # Scheme (HTTP, HTTPS, FTP and SFTP):
                        regex += r'(?:(https?|s?ftp):\/\/)?'

                        # www:
                        regex += r'(?:www\.)?'

                        regex += r'('

                        # Host and domain (including ccSLD):
                        regex += r'(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)'

                        # TLD:
                        regex += r'([A-Z]{2,6})'

                        # IP Address:
                        regex += r'|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

                        regex += r')'

                        # Port:
                        regex += r'(?::(\d{1,5}))?'

                        # Query path:
                        regex += r'(?:(\/\S+)*)'

                        regex += r')'

                        # urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', stepObj.image_link)
                        urls = re.findall(regex, stepObj.image_link)
                        if urls and False:
                            x = 1
                            for url in urls:
                                html += '<div> <a href="' + url + '"> ' + url + '</a> </div>'

                        else:
                            html += stepObj.image_link

            testcase.imgLink = html

    imgLink = fields.Text(
        'Image Link',
        compute='_compute_imgLink', track_visibility='onchange')

    testproject_id = fields.Many2one('testcase_management.project', string='Test Project', copy=True)

    # test step compute

    # test case and task have relationship many2many

    # task_ids = fields.Many2many(
    #     'project.task',  # related= (model name)
    #     'testcase_management_task_rel',  # relation= (table name)
    #     'testcase_management_id',  # column1= ("this" field)
    #     'task_id',  # column2= ("other" field)
    #     string='Tasks',
    #     # Relational field attributes:
    #     auto_join=True,
    #     context={},
    #     domain=[],
    #     ondelete='cascade',
    # )

    # @api.onchange('actualResult')
    # def _onchange_actualResult(self):
    #     if self.actualResult:
    #         self._message_log(self.actualResult , False, 'comment')

    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as image for the asset, limited to 1024x1024px.",
                          copy=True)
    img_ids = fields.One2many('testcase_management.img', 'test_id', copy=True)

    @api.model
    def create(self, values):
        projectId = None
        if 'project_id' not in values:
            projectId = self._context.get('active_id')
            values['project_id'] = projectId
        # set default value for testcase
        if not values['user_id']:
            userId = self._context.get('uid')

            values['user_id'] = userId

        # suit id , if user does not choose an suit it, then use the lastest one
        if not values['suit_id']:
            testcase_name = self.env['testcase_management.suit'].search([('project_id', '=', projectId)],
                                                                        order='id desc', limit=2)
            # a = testcase_name[0]
            if testcase_name:
                a = testcase_name[0]
                values['suit_id'] = a.id

        testcase = super(testcase_management, self).create(values)
        testcase.suit_id.write({
            'project_id': testcase.project_id.id
        })

        sequenModel = self.env['ir.sequence']

        testProject = self.env['testcase_management.project']
        # Before write logic

        project_model = testcase.project_id

        # if not project_model.code:
        #     raise ValidationError(_("Project must have a code. Contact with the project manager to set it up"))
        if project_model:
            project_name = project_model.name
            sequenceCode = ''.join(['increment_', 'testcode_', str(project_model.id)])
            projectSequenceId = project_model.sequenceTestId
            prefix = ''.join(['T', str(project_model.code), '-'])

            if not projectSequenceId:

                # sequenModel = self.env['ir.sequence'].search([('code','=',sequenceCode)])

                sObject = sequenModel.sudo().create({'name': project_name,
                                                     'code': sequenceCode,
                                                     'prefix': prefix,
                                                     'padding': 3
                                                     })

                # project_model.update({'sequenceId',sequenModel.id})
                for si in sObject:
                    theId = si.id
                    project_model.sudo().sequenceTestId = si.id

            sequenModel = self.env['ir.sequence'].browse(project_model.sequenceTestId)
            # sequenModel = self.env['ir.sequence'].browse(64)

            for sequenceObj in sequenModel:
                sc = sequenceObj.code

                # update order no
                # testcase.update({orderno:orderno})
                testcase.orderno = str(self.env['ir.sequence'].next_by_code(sc))

            # test project
            projectTestId = project_model.projectTestId

            if not projectTestId:
                testProjectBean = testProject.sudo().create({'name': project_name,
                                                             'note': 'Test Project',
                                                             'project_id': project_model.id

                                                             })
                project_model.sudo().projectTestId = testProjectBean.id
            # #retrieve test project
            testProj = self.env['testcase_management.project'].browse(project_model.projectTestId)

            if testProj:
                for x in testProj:
                    testcase.testproject_id = x.id
        return testcase

    # copy the test case will copy the test step
    # @api.multi
    # @api.returns('self', lambda value: value.id)
    # def copy(self, default=None):
    #     self.ensure_one()
    #     if not default:
    #         default = {}
    #     default.update({
    #         'state': '',
    #         'dev_state': '',
    #         'project_id': '',
    #         'task_id': '',
    #     })
    #     vals = self.copy_data(default)[0]
    #     x = vals
    #
    #     # vals['task']
    #     # To avoid to create a translation in the lang of the user, copy_translation will do it
    #     new = self.with_context(lang=None).create(vals)
    #
    #     self.with_context(from_copy_translation=True).copy_translations(new, excluded=default or ())
    #
    #     testId = self.id
    #
    #     stepIds = self.step_ids
    #
    #     if stepIds:
    #         stepModel = self.env['testcase_management.step']
    #
    #         for step in stepIds:
    #             x = step.test_data
    #             # create new test step
    #             stepBean = stepModel.create(
    #                 {'name': step.name, 'test_data': step.test_data, 'expected_result': step.expected_result,
    #                  'actual_result': step.actual_result, 'image_link': step.image_link, 'note': step.note,
    #                  'test_id': new.id, 'user_id': False, 'suit_id': False})
    #
    #     return new

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(testcase_management, self).copy(default)
        # res.name = ''
        for follower in self.message_follower_ids:
            res.message_subscribe(partner_ids=follower.partner_id.ids, subtype_ids=follower.subtype_ids.ids)
        # res.project_id = False
        return res

    def unlink(self):
        return super(testcase_management, self).unlink()

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        y = self.env.context
        active_id = self.env.context.get('active_id')

        if domain:
            for filterItem in domain:
                for item in filterItem:

                    if 're_fixed_failed_fixed' == item:
                        query = 'SELECT "testcase_management_testcase_management".id FROM "testcase_management_testcase_management" WHERE "testcase_management_testcase_management"."project_id" = %d  AND "testcase_management_testcase_management"."state" =\'1\' AND "testcase_management_testcase_management"."dev_state" = \'0\' AND ( "testcase_management_testcase_management"."lastUpdatedState" < "testcase_management_testcase_management"."lastDevUpdatedState" OR  ("testcase_management_testcase_management"."lastUpdatedState" is null AND  "testcase_management_testcase_management"."lastDevUpdatedState" is not null) )' % (
                            active_id)
                        self.env.cr.execute(query)
                        results = self.env.cr.fetchall()
                        ids = results
                        domain = [('id', 'in', ids)]
                        return super(testcase_management, self).search_read(domain, fields, offset, limit, order)

                    # if 're_fixed' == item:
                    #     query = 'SELECT "testcase_management_testcase_management".id FROM "testcase_management_testcase_management" WHERE "testcase_management_testcase_management"."project_id" = %d  AND "testcase_management_testcase_management"."state" =\'1\' AND "testcase_management_testcase_management"."dev_state" = \'0\' AND ( "testcase_management_testcase_management"."lastUpdatedState" < "testcase_management_testcase_management"."lastDevUpdatedState" OR  ("testcase_management_testcase_management"."lastUpdatedState" is null AND  "testcase_management_testcase_management"."lastDevUpdatedState" is not null) )' % (active_id)
                    #     self.env.cr.execute(query)
                    #     results = self.env.cr.fetchall()
                    #     ids = results
                    #     domain = [('id', 'in', ids)]
                    #     return super(testcase_management, self).search_read(domain, fields, offset, limit, order)

                    # Re tesed filter
                    if 're_tested_failed_fixed' == item:
                        query = 'SELECT "testcase_management_testcase_management".id FROM "testcase_management_testcase_management" WHERE "testcase_management_testcase_management"."project_id" = %d  AND "testcase_management_testcase_management"."state" =\'1\' AND "testcase_management_testcase_management"."dev_state" = \'0\' AND ( "testcase_management_testcase_management"."lastUpdatedState" > "testcase_management_testcase_management"."lastDevUpdatedState" OR  ("testcase_management_testcase_management"."lastUpdatedState" is not null AND  "testcase_management_testcase_management"."lastDevUpdatedState" is  null) )' % (
                            active_id)
                        self.env.cr.execute(query)
                        results = self.env.cr.fetchall()
                        ids = results
                        domain = [('id', 'in', ids)]
                        return super(testcase_management, self).search_read(domain, fields, offset, limit, order)
                    #
                    # if 're_tested' == item:
                    #     query = 'SELECT "testcase_management_testcase_management".id FROM "testcase_management_testcase_management" WHERE "testcase_management_testcase_management"."project_id" = %d  AND "testcase_management_testcase_management"."state" =\'1\' AND "testcase_management_testcase_management"."dev_state" = \'0\' AND ( "testcase_management_testcase_management"."lastUpdatedState" > "testcase_management_testcase_management"."lastDevUpdatedState" OR  ("testcase_management_testcase_management"."lastUpdatedState" is not null AND  "testcase_management_testcase_management"."lastDevUpdatedState" is  null) )' % (active_id)
                    #     self.env.cr.execute(query)
                    #     results = self.env.cr.fetchall()
                    #     ids = results
                    #     domain = [('id', 'in', ids)]
                    #     return super(testcase_management, self).search_read(domain, fields, offset, limit, order)

        if active_id:
            if len(domain) > 0:
                domain.extend([('project_id', '=', active_id)])
                # self.env.context.update({'project_id': active_id})
                # self.with_context(project_id=active_id,active_model='project.project')


            else:
                domain = [('project_id', '=', active_id)]
                self.with_context(project_id=active_id, active_model='project.project', default_project_id=active_id)

            return super(testcase_management, self).search_read(domain, fields, offset, limit, order)
        else:
            return super(testcase_management, self).search_read(domain, fields, offset, limit, order)

    # @api.multi
    def write(self, values):
        # Before write logic
        if 'state' in values.keys():
            if values['state']:
                values['lastUpdatedState'] = fields.Datetime.now()

        if 'markAsRetest' in values.keys():

            if values['markAsRetest']:
                values['lastUpdatedState'] = fields.Datetime.now()
                # values['markAsRetest'] = False
        # the dev state
        if 'markAsReFixed' in values.keys():

            if values['markAsReFixed']:
                values['lastDevUpdatedState'] = fields.Datetime.now()
                # values['markAsReFixed'] = False

        tcs = super(testcase_management, self).write(values)
        for rec in self:
            current_test_case = self.env['testcase_management.testcase_management'].browse(rec.id)
            if current_test_case.suit_id:
                current_test_case.suit_id.write({
                    'project_id': current_test_case.project_id.id
                })

        stepTestNote = ''

        if 'step_ids' in values.keys():

            for stepDic in values['step_ids']:

                if stepDic[2]:
                    for key, vals in stepDic[2].items():
                        if vals:
                            x = key
                            y = vals

                            stepTestNote += str(key) + ': ' + str(vals) + '\n'

            # for item in self:
            #     self._message_log('Note note' , False, 'comment')
            self._message_log(body=stepTestNote, message_type= 'comment')

        return tcs

    def logHistory(self):
        self._message_log(body='log note', message_type= 'comment')

    def open_rec(self):
        return {
            'view_mode': 'form',
            'res_model': 'testcase_management.testcase_management',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'flags': {'form': {'action_buttons': True}}

        }

    active = fields.Boolean('Active', default=True, tracking=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active

    def force_archive(self):
        for record in self:
            if record.active:
                record.active = not record.active

    def force_un_archive(self):
        for record in self:
            if not record.active:
                record.active = not record.active


class DuplicateTestcase(models.TransientModel):
    _name = 'duplicate.testcase'
    project_id = fields.Many2one('project.project', string='Duplicate Project')
    task_ids = fields.Many2one('project.task',string='#Task')
    @api.model
    def get_default_testcase(self):
        if self._context.get('active_ids'):
            return self.env['testcase_management.testcase_management'].browse(self._context.get('active_ids'))

    duplicate_testcase = fields.Many2many('testcase_management.testcase_management', default=get_default_testcase)
    def copy_testcase(self):
        defaults = {
            'project_id': self.project_id.id,
            'state': '',
        }

        testcase = self.env['testcase_management.testcase_management']
        for e in self.duplicate_testcase:
            a = e.copy(default=defaults)
            a.update({
                'project_id': self.project_id,
            })
            if self.task_ids:
                self.task_ids.write({
                    'test_id':[(4, a.id)]
                })
            testcase += a


