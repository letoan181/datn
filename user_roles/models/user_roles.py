from odoo import fields, models, api, _
from odoo.exceptions import UserError


class UserRoles(models.Model):
    _name = 'user.roles'
    _description = 'User Roles'
    manager_id = fields.Many2many('res.users', string='User')
    line_user_ids = fields.One2many('user.roles.line', 'role_id', string='Role user line')
    name = fields.Char(string='Name')
    groups_user = fields.Many2many('res.groups', string='GroupUser')

    @api.model
    def create(self, vals):
        check_user = self.check_user_in_user_role()
        user_role = super(UserRoles, self).create(vals)

        # check user đã thuộc 1 user role hay chưa
        for all_user_role in check_user:
            for user_pice in user_role.manager_id:
                if all_user_role == user_pice:
                    raise UserError('User already exists in other User role records')
        if user_role.manager_id and user_role.groups_user:
            for group in user_role.groups_user:
                for user in user_role:
                    group.sudo().update({
                        'users': [(4, user.id)]
                    })
        return user_role

    def write(self, vals):
        self = self.sudo()
        user_old = self.update_roles()

        group_old = self.groups_old()
        user_line_old = self.del_user()
        res = super(UserRoles, self).write(vals)

        #Xóa group trong user role tự động xóa user ra khỏi group
        if self.groups_user:
            group_unlink = group_old - self.groups_user
            for user_del in self.update_roles():
                group_unlink.sudo().update({
                    'users': [(3, user_del.id)]
                })

        # Thêm và Xóa User trong user roles thì user tự động thêm, xóa khỏi groups
        if self.line_user_ids.user_id:
            user_line_unlink = user_line_old - self.line_user_ids.user_id
        else:
            user_line_unlink = user_line_old
        for group in self.groups_user:
            for list_user_line in user_line_unlink:
                group.sudo().update({
                    'users': [(3, list_user_line.id)]
                })
        for group in self.groups_user:
            for user_add in self.line_user_ids.user_id:
                if user_add.independent:
                    raise UserError(_("Not add user in groups"))
                if group.name == "#1 . Admin User Roles":
                    continue
                group.sudo().update({
                    'users': [(4, user_add.id)]
                })

        # Thêm và xóa cho user được quyền assign nhiệm vụ tự động thêm và xóa user ra khoi gruops
        if self.manager_id or self.groups_user:

            user_unlink = user_old - self.manager_id
            if len(user_unlink) > 0:
                for group in self.groups_user:
                    for list_user in user_unlink:
                        list_user.set_user_role = False
                        group.sudo().update({
                            'users': [(3, list_user.id)]
                        })
            for group in self.groups_user:
                for user in self.manager_id:
                    user.set_user_role = True
                    if user.independent:
                        raise UserError(_("Not add user in groups"))
                    else:
                        group.sudo().update({
                            'users': [(4, user.id)]
                        })
            return res

        # function check tồn tại user

    def check_user_in_user_role(self):
        list_user_check = []
        user_role = self.env['user.roles'].search([])
        for rec in user_role:
            for result in rec.manager_id:
                list_user_check.append(result)
        return list_user_check

    def groups_old(self):
        return self.groups_user

    def update_roles(self):
        return self.manager_id

    def del_user(self):
        return self.line_user_ids.user_id
