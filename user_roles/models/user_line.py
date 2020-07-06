from odoo import models, fields, _


class UserRolesLine(models.Model):
    _name = 'user.roles.line'
    _description = 'User Roles Line'
    name = fields.Char(string='Name')
    user_id = fields.Many2one('res.users', string='User', domain=[('set_user_role', '=', False), ('independent', '=', False)])
    role_id = fields.Many2one('user.roles', string='Role', ondelete='cascade')

    def action_user_roles_change_password_view(self):
        view_id = self.env.ref('user_roles.user_roles_change_password_wizard_view').id
        return {'type': 'ir.actions.act_window',
                'name': _('User Roles Change Password'),
                'res_model': 'change.password.login',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [[view_id, 'form']]
                }
