from odoo import fields, models


class TestCaseTask(models.Model):
    _inherit = 'project.task'

    # test case
    # testcase_management_ids = fields.Many2many('testcase_management.testcase_management', String='TestCases')
    test_id = fields.One2many('testcase_management.testcase_management', 'task_id')
