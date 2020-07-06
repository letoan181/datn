import logging

from odoo import api, fields, models, _


class TestCaseProject(models.Model):
    _inherit = 'project.project'

    testcode = fields.Char('TestCode')

    sequenceTestId = fields.Integer('Sequence Test Number')
    projectTestId = fields.Integer('Project Test Number')

    # test_project = fields.One2many('testcase_management.project', 'project_id')
    total_testcase = fields.Integer(string="Total test case", compute="compute_test_report", default=0)
    total_testcase_pass = fields.Integer(string="Total test case pass", compute="compute_test_report", default=0)
    total_testcase_failed = fields.Integer(string="Total test case failed", compute="compute_test_report", default=0)
    total_testcase_pending = fields.Integer(string="Total test case pending", compute="compute_test_report", default=0)
    total_testcase_mark_retest_failed = fields.Integer(string="Total test case mark re-test failed", compute="compute_test_report", default=0)
    total_testcase_dev_reject = fields.Integer(string="Total test case dev reject", compute="compute_test_report", default=0)
    total_testcase_re_duplicate = fields.Integer(string="Total test case mark reduplicate", compute="compute_test_report", default=0)
    percent_testcase_failed = fields.Float(string="% test case failed", compute="compute_test_report")
    percent_testcase_pending = fields.Float(string="% test case pending", compute="compute_test_report")
    percent_testcase_pass = fields.Float(string="% test case pass", compute="compute_test_report")

    def compute_test_report(self):
        for rec in self:
            rec.total_testcase = 0
            rec.total_testcase_pass = 0
            rec.total_testcase_failed = 0
            rec.total_testcase_pending = 0
            rec.total_testcase_re_duplicate = 0
            rec.total_testcase_mark_retest_failed = 0
            rec.total_testcase_dev_reject = 0
            rec.percent_testcase_failed = 0
            rec.percent_testcase_pending = 0
            rec.percent_testcase_pass = 0
            test_case_ids = self.env['testcase_management.testcase_management'].sudo().search([('project_id', '=', rec.id)])
            if test_case_ids:
                total_testcase = 0
                total_testcase_pass = 0
                total_testcase_failed = 0
                total_testcase_pending = 0
                total_testcase_mark_retest_failed = 0
                total_testcase_dev_reject = 0
                total_testcase_re_duplicate = 0
                for test_case in test_case_ids:
                    total_testcase += 1
                    if test_case.state == '0':
                        total_testcase_pass += 1
                    if test_case.state == '1':
                        total_testcase_failed += 1
                    if test_case.state in ['2', '3']:
                        total_testcase_pending += 1
                    if test_case.state == '1' and test_case.markAsRetest:
                        total_testcase_mark_retest_failed += 1
                    if test_case.dev_state in ['1', '2', '3']:
                        total_testcase_dev_reject += 1
                rec.total_testcase = total_testcase
                rec.total_testcase_pass = total_testcase_pass
                rec.total_testcase_failed = total_testcase_failed
                rec.total_testcase_pending = total_testcase_pending
                rec.total_testcase_re_duplicate = total_testcase_re_duplicate
                rec.total_testcase_mark_retest_failed = total_testcase_mark_retest_failed
                rec.total_testcase_dev_reject = total_testcase_dev_reject
                rec.percent_testcase_failed = (total_testcase_failed / total_testcase) * 100
                rec.percent_testcase_pending = (total_testcase_pending / total_testcase) * 100
                rec.percent_testcase_pass = (total_testcase_pass / total_testcase) * 100

    def get_statistic(self, ids):
        project_id = self.env.context.get('project_id')
        _logger = logging.getLogger(__name__)

        _logger.info('get statistic')
        projectTest_id = self.id

        testcase_name = self.env['testcase_management.project'].search([('project_id', '=', projectTest_id)],
                                                                       order='id desc',
                                                                       limit=1)
        html = ''
        i = 0
        if testcase_name:
            p = testcase_name[0]
            html = "<div> Number of testcase <b> %s</b> </div> <div> Failed <b>%s</b> </div> <div>Passed <b>%s</b> </div> <div>Fixed <b>%s</b> </div> <div> Untested <b>%s</b></div> " % (
                p.all_test_count, p.failed_count, p.passed_count, p.fixed_count, p.untested_count)

        return html

    def action_view_testcase(self):
        _logger = logging.getLogger(__name__)

        _logger.info('view all test case')
        ctx = dict(self._context)
        ctx.update({'project_id': self.id})
        ctx.update({'default_project_id': self.id})
        ctx.update({'3_project_id': self.id})
        ctx.update({'active_id': self.id})

        ctx.update({'name': 'Testcases management for ' + self.name})

        # testcase_ids = self.env['testcase_management.testcase_management'].with_context(active_test=False).search([('project_id', '=', self.id)]).ids

        action = self.env['ir.actions.act_window'].for_xml_id('testcase_management',
                                                              'testcase_management_action_window')
        action['domain'] = [('project_id', '=', self.id)]
        action['name'] = _('Testcase managements  of %s') % (self.name,)
        action['display_name'] = _('Testcase managements  of %s') % (self.name,)

        # action_context = safe_eval(action['context']) if action['context'] else {}
        # action_context.update(self._context)
        # action_context['search_default_project_id'] = self.id
        # action_context.pop('group_by', None)
        return dict(action, context=ctx)
