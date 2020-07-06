from odoo import models, fields, api


class IntangibleAssets(models.Model):
    _name = 'intangible.asset'
    _description = 'Virtual Assets'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    description = fields.Html(string="Description", )
    employee_ids = fields.Many2many(comodel_name="hr.employee", string="Employee")
    assign_date = fields.Date("Assign Date")
    employee_approve_status = fields.One2many(comodel_name='employee.intangible.asset.status',
                                              string='Employee approve status', inverse_name='intangible_asset_id',
                                              store=True)
    waiting_for_inventory = fields.Boolean('Waiting for Inventory')
    disable_return_button = fields.Boolean("Disable Assign Button", compute='compute_dis_return_btn')
    disable_approve_button = fields.Boolean("Disable Approve Button", compute='compute_dis_approve_btn')

    def compute_dis_return_btn(self):
        employee_approve_status = self.env['employee.intangible.asset.status'].search(
            [('employee_id', '=', self.env.user.employee_ids.id), ('intangible_asset_id', '=', self.id)])
        if employee_approve_status:
            if self.env.user.has_group(
                    'intangible_asset_management.group_user_intangible_asset') is True and employee_approve_status.status in [
                'return', 'unapproved', 'refuse']:
                self.disable_return_button = True
            elif self.env.user.has_group(
                    'intangible_asset_management.group_manager_intangible_asset') is True and employee_approve_status.status not in [
                'approved']:
                self.disable_return_button = True
            else:
                self.disable_return_button = False
        else:
            self.disable_return_button = True

    def compute_dis_approve_btn(self):
        employee_approve_status = self.env['employee.intangible.asset.status'].search(
            [('employee_id', '=', self.env.user.employee_ids.id), ('intangible_asset_id', '=', self.id)])
        if employee_approve_status:
            if self.env.user.has_group(
                    'intangible_asset_management.group_user_intangible_asset') is True and employee_approve_status.status in [
                'approved', 'return', 'refuse']:
                self.disable_approve_button = True
            else:
                self.disable_approve_button = False
        else:
            self.disable_approve_button = True

    @api.onchange('employee_ids')
    def onchange_employee_approve_status(self):
        if not self._origin.id:
            employee_approve_status = []
        else:
            employee_approve_status = self.env['employee.intangible.asset.status'].search(
                [('intangible_asset_id', '=', self._origin.id)])
        employee_ids_old = []
        employee_approve_status_old = []
        for e in employee_approve_status:
            if e.employee_id in self.employee_ids:
                employee_approve_status_old.append({
                    'employee_id': e.employee_id,
                    'intangible_asset_id': self._origin.id,
                    'status': e.status
                })
                employee_ids_old.append(e.employee_id)

        for f in self.employee_ids:
            if f in employee_ids_old:
                continue
            else:
                if f.user_id.id == self.env.user.id:
                    employee_approve_status_old.append({
                        'employee_id': f.id,
                        'intangible_asset_id': self._origin.id,
                        'status': 'approved'
                    })
                else:
                    employee_approve_status_old.append({
                        'employee_id': f.id,
                        'intangible_asset_id': self._origin.id,
                        'status': 'unapproved'
                    })

        self.employee_approve_status = False

        self.employee_approve_status = employee_approve_status_old

    def action_receive(self):
        self.ensure_one()
        if self.env.user.has_group('intangible_asset_management.group_user_intangible_asset'):
            employee_approve_status = self.env['employee.intangible.asset.status'].search(
                [('employee_id', '=', self.env.user.employee_ids.id), ('intangible_asset_id', '=', self.id)])
            employee_approve_status.write({
                'status': 'approved'
            })
            self.message_post(
                body="%s has been received successfully by %s" % (self.name, employee_approve_status.employee_id.name))

    def action_refuse(self):
        self.ensure_one()
        if self.env.user.has_group('intangible_asset_management.group_user_intangible_asset'):
            employee_approve_status = self.env['employee.intangible.asset.status'].search(
                [('employee_id', '=', self.env.user.employee_ids.id), ('intangible_asset_id', '=', self.id)])
            employee_approve_status.write({
                'status': 'refuse'
            })
            self.message_post(
                body="%s has refused to receive %s" % (employee_approve_status.employee_id.name, self.name))

    def action_return(self):
        self.ensure_one()
        employee_approve_status = self.env['employee.intangible.asset.status'].search(
            [('employee_id', '=', self.env.user.employee_ids.id), ('intangible_asset_id', '=', self.id)])
        employee_approve_status.write({
            'status': 'return'
        })
        self.message_post(
            body="%s has sent a return request for %s" % (employee_approve_status.employee_id.name, self.name))

    def write(self, vals):
        # normal employee can not update employees
        if 'employee_ids' in vals:
            for rec in self:
                # update follower
                partner_ids_old = []
                employee_ids_old = []
                if rec.employee_ids:
                    for e in rec.employee_ids:
                        partner_ids_old.append(e.user_id.partner_id.id)
                        employee_ids_old.append(e.id)
                if partner_ids_old:
                    rec.sudo().message_unsubscribe(partner_ids=partner_ids_old)

                partner_ids_new = []
                for e in vals['employee_ids'][0][2]:
                    partner_ids_new.append(self.env['hr.employee'].search([('id', '=', e)]).user_id.partner_id.id)
                rec.sudo().message_subscribe(partner_ids=partner_ids_new)

                # send message to users when update who to use virtual asset
                for e in vals['employee_ids'][0][2]:
                    if e in employee_ids_old:
                        continue
                    else:
                        rec.sudo().message_post(body="%s was assigned to %s. Please approve" % (
                            rec.name, self.env['hr.employee'].search([('id', '=', e)]).name))

                # send message to employee is disabled virtual asset

                for e in rec.employee_ids:
                    if e.id not in vals['employee_ids'][0][2]:
                        # add noti to follower
                        rec.sudo().message_post(body="%s is removed on %s" % (e.name, rec.name))
                        # send message to employee is deleted
                        post_vars = {'subject': "Virtual Assets",
                                     'partner_ids': [e.user_id.partner_id.id], }
                        # Send messages to previous users
                        thread_pool = self.env.get('mail.thread')
                        thread_pool.message_post(
                            body="Manager has removed you on %s" % rec.name,
                            type="notification",
                            subtype="mt_comment",
                            **post_vars)

        res = super(IntangibleAssets, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        intangible_assets = super(IntangibleAssets, self).create(vals)
        # add follower and send message
        partner_ids = []
        user_ids = []
        if intangible_assets.employee_ids:
            for e in intangible_assets.employee_ids:
                partner_ids.append(e.user_id.partner_id.id)
                user_ids.append(e)
        if partner_ids:
            intangible_assets.message_subscribe(partner_ids=partner_ids)
            for e in user_ids:
                intangible_assets.message_post(
                    body="%s was assigned to %s. Please approve" % (intangible_assets.name, e.name))
        # auto approve assets if create user in employees be assign virtual asset
        if self.env.user.employee_ids in intangible_assets.employee_ids:
            for e in intangible_assets.employee_approve_status:
                if e.employee_id.id == self.env.user.employee_ids.id:
                    e.status = 'approved'
        return intangible_assets

    def unlink(self):
        for rec in self:
            follower = self.env['mail.followers'].search(
                [('res_model', '=', 'intangible.asset'), ('res_id', '=', rec.id)])
            for e in follower:
                post_vars = {'subject': "Virtual Assets",
                             'partner_ids': [e.partner_id.id], }
                # Send messages to previous users
                thread_pool = self.env.get('mail.thread')
                thread_pool.message_post(
                    body="Manager has removed %s. Now, you can't access it." % rec.name,
                    type="notification",
                    subtype="mt_comment",
                    **post_vars)
            super(IntangibleAssets, rec).unlink()


class EmployeeIntangibleAssetStatus(models.Model):
    _name = 'employee.intangible.asset.status'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    intangible_asset_id = fields.Many2one(comodel_name='intangible.asset', string='Intangible Asset', )
    status = fields.Selection(string="Status",
                              selection=[('unapproved', 'Unapproved'), ('approved', 'Approved'), ('refuse', 'Refuse'),
                                         ('return', 'Return'), ('returned', 'Returned')], default='unapproved')

    def accept_return(self):
        self.ensure_one()
        post_vars = {'subject': "Virtual Assets",
                     'partner_ids': [self.employee_id.user_id.partner_id.id], }
        # Send messages to previous users
        thread_pool = self.env.get('mail.thread')
        thread_pool.message_post(
            body="HR has accepted the return request for %s" % self.intangible_asset_id.name,
            type="notification",
            subtype="mt_comment",
            **post_vars)
        partner_ids = [self.employee_id.user_id.partner_id.id]
        self.intangible_asset_id.message_unsubscribe(partner_ids=partner_ids)
        self.intangible_asset_id.employee_ids = [(3, self.employee_id.id,)]
        self.intangible_asset_id.message_post(
            body="%s has accepted %s\'s request" % (
                self.env.user.name, self.employee_id.name))
        self.unlink()

    def decline_return(self):
        self.ensure_one()
        if self.status == 'return':
            self.status = 'approved'
            self.intangible_asset_id.message_post(
                body="%s has refused %s's request to return %s to company" % (
                    self.env.user.name, self.employee_id.name, self.intangible_asset_id.name))
        elif self.status == 'refuse':
            self.status = 'unapproved'
            self.intangible_asset_id.message_post(
                body="%s does not accept %s's refusal" % (
                    self.env.user.name, self.employee_id.name))
