from odoo import fields, models, tools, _, api


class AddFollowers(models.TransientModel):
    _name = "add.followers"

    def _default_sessions(self):
        return self.env['project.project'].browse(self._context.get('active_ids'))

    project_ids = fields.Many2many('project.project',
                                   string="Sessions Project", required=True, default=_default_sessions)

    partner_ids = fields.Many2many("res.partner", string=_("Add users follow Project"))

    def add_followers(self):
        for project_id in self.project_ids:
            existing_followers_id = [val.partner_id.id for val in project_id.message_follower_ids]
            for partner_id in self.partner_ids:
                if not (partner_id.id in existing_followers_id):
                    self.env['mail.followers'].create({
                        'res_model': 'project.project',
                        'res_id': project_id.id,
                        'partner_id': partner_id.id

                    })
        return {'type': 'ir.actions.act_window_close'}

    def un_followers(self):
        for project_id in self.project_ids:
            for partner_id in self.partner_ids:
                self.env['mail.followers'].search(
                    [('res_model', '=', 'project.project'), ('res_id', '=', project_id.id),
                     ('partner_id', '=', partner_id.id)]).unlink()
        return {'type': 'ir.actions.act_window_close'}
