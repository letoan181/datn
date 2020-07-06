from odoo import api, fields, models


class MassActionChangeTaskTestCase(models.TransientModel):
    _name = "change.task.testcase"

    test_case_ids = fields.Many2many("testcase_management.testcase_management", 'change_task_testcase_rel', 'change_id', 'testcase_id', string="Test case")

    project_id = fields.Many2one(string="Project", comodel_name="project.project")

    task_id = fields.Many2one(string="Task destination", comodel_name="project.task")

    def confirm_change_task(self):
        if self.test_case_ids:
            for testcase in self.test_case_ids:
                testcase.project_id = self.project_id
                testcase.task_id = self.task_id
        return {'type': 'ir.actions.act_window_close'}
