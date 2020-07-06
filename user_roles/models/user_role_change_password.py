from odoo import models, fields, api


class ChangePassword(models.Model):
    _name = 'change.password.login'

    new_password = fields.Char(string='New Passwords')

    def _default_user_ids(self):
        return self.env['user.roles.line'].browse(self._context.get('active_id'))

    user_ids = fields.Many2one('user.roles.line', string='User', default=_default_user_ids, readonly=True)

    def change_password_button(self):
        if self.new_password is not None:
            res = self.env['user.roles.line'].browse(self._context.get('active_id'))
            self._cr.execute(''' UPDATE res_users SET password = %s WHERE id = %s''', [self.new_password, res.user_id.id])
        return {'type': 'ir.actions.act_window_close'}