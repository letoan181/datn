from odoo import models


class MailFollowers(models.Model):
    _inherit = "mail.followers"

    def unfollow_not_user_in_project_task(self):
        # unfollow non user from project,task
        unfollow_not_user_in_project_task = self.env['mail.followers'].search([('res_model', '=', 'project.task'), ('partner_id.user_ids', '=', False)])
        unfollow_not_user_in_project_project = self.env['mail.followers'].search([('res_model', '=', 'project.project'), ('partner_id.user_ids', '=', False)])

        unfollow_not_user_in_project_task.unlink()
        unfollow_not_user_in_project_project.unlink()

        # unfollow inactive user partner from project,task
        inactive_user = self.env['res.users'].search([('active', '=', False)])
        inactive_user_partner = [e.partner_id for e in inactive_user]
        unfollow_not_user_in_project_task = self.env['mail.followers'].search([('res_model', '=', 'project.task'), ('partner_id', 'in', [e.id for e in inactive_user_partner])])
        unfollow_not_user_in_project_project = self.env['mail.followers'].search([('res_model', '=', 'project.project'), ('partner_id', 'in', [e.id for e in inactive_user_partner])])
        unfollow_not_user_in_project_task.unlink()
        unfollow_not_user_in_project_project.unlink()

