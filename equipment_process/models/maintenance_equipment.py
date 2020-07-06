from datetime import date

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.http import request


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    equipment_ids = fields.One2many(comodel_name="maintenance.equipment", inverse_name="employee_id",
                                    string="Equipment", required=False)


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    state = fields.Selection([('unapproved', 'Unapproved'), ('approved', 'Approved'), ('refused', 'Refused'),
                              ('returned', 'Return to Company')],
                             default='unapproved', track_visibility='onchange')
    waiting_for_inventory = fields.Boolean('Return to inventory', readonly=True, default=False)
    disable_assign_button = fields.Boolean("Disable Assign Button", compute='compute_dis_assign_btn', default=False)
    employee_not_inventory = fields.Many2many('hr.employee', compute='_get_employee_not_inventory', store=False)
    assign_to_employee = fields.Many2many('hr.employee', compute='get_employees', store=False)

    @api.onchange('department_id')
    def get_employees(self):
        if self.equipment_assign_to == 'other':
            self.assign_to_employee = self.env['hr.employee'].search([('department_id', '=', self.department_id.id)])
        else:
            self.assign_to_employee = self.env['hr.employee'].search([])

    @api.onchange('employee_id')
    def cannot_change_employee(self):
        if self.state != 'unapproved':
            raise UserError('You cannot change the employee who has been assigned this equipment')

    @api.onchange('department_id')
    def cannot_change_department(self):
        if self.state != 'unapproved':
            raise UserError('You cannot change the department which has been assigned this equipment')

    def compute_dis_assign_btn(self):
        inventory = request.env.ref('equipment_process.inventory_master').id
        if self.env.user.has_group(
                'equipment_process.group_manager_equipment') == True and self.employee_id.id == inventory:
            self.disable_assign_button = True
        elif self.env.user.has_group(
                'equipment_process.group_manager_equipment') == True and self.employee_id.id != inventory:
            self.disable_assign_button = False
        elif self.env.user.has_group(
                'equipment_process.group_user_equipment') == True and self.waiting_for_inventory == True:
            self.disable_assign_button = True
        elif self.employee_id.id == inventory:
            self.disable_assign_button = True
        else:
            self.disable_assign_button = False

    def action_receive(self):
        for rec in self:
            if rec.waiting_for_inventory == True and rec.state in ['unapproved', 'refused', 'returned']:
                if rec.employee_id:
                    if rec.employee_id.user_id.partner_id.id:
                        post_vars = {'subject': "Maintenance Equipment",
                                     'partner_ids': [rec.employee_id.user_id.partner_id.id], }
                        # Send messages to previous users
                        rec.message_post(
                            body="HR has accepted that your %s has been returned to the company's inventory" % (
                                rec.name),
                            type="notification",
                            subtype="mt_comment",
                            **post_vars)
                    # assign to inventory employee
                    inventory = request.env.ref('equipment_process.inventory_master').id
                    rec.sudo().write({
                        'state': 'unapproved',
                        'assign_date': date.today(),
                        'employee_id': inventory,
                        'waiting_for_inventory': False,
                        'disable_assign_button': True
                    })
                else:
                    post_vars = {'subject': "Maintenance Equipment",
                                 'partner_ids': [rec.department_id.manager_id.user_id.partner_id.id], }
                    # Send messages to previous users
                    thread_pool = rec.env.get('mail.thread')
                    thread_pool.message_post(
                        body="HR has accepted that your %s has been returned to the company's inventory" % (rec.name),
                        type="notification",
                        subtype="mt_comment",
                        **post_vars)
                    # assign to inventory employee
                    inventory = request.env.ref('equipment_process.inventory_master').id
                    rec.sudo().write({
                        'state': 'unapproved',
                        'assign_date': date.today(),
                        'equipment_assign_to': 'employee',
                        'employee_id': inventory,
                        'department_id': False,
                        'waiting_for_inventory': False,
                        'disable_assign_button': True
                    })
            else:
                rec.sudo().write({
                    'state': 'approved',
                    'assign_date': date.today(),
                })
                rec.message_post(body="%s approved to receive %s" % (rec.env.user.employee_ids.name, rec.name))

    def action_refuse(self):
        self.ensure_one()
        if self.waiting_for_inventory == True:
            self.sudo().write({
                'state': 'approved',
                'waiting_for_inventory': False,
                'disable_assign_button': False
            })
            self.message_post(body="%s refused request return %s to company" % (
                self.env.user.employee_ids.name, self.name))
        else:
            self.sudo().write({
                'state': 'refused',
                'waiting_for_inventory': True,
                'assign_date': date.today(),
                'disable_assign_button': True
            })
            self.message_post(body="%s refused to receive %s" % (self.env.user.employee_ids.name, self.name))

    def action_return(self):
        self.ensure_one()
        self.sudo().write({
            'state': 'returned',
            'assign_date': date.today(),
            'waiting_for_inventory': True
        })
        self.message_post(body="%s has returned %s to company, waiting for Manager Equipment to approve" % (
            self.env.user.employee_ids.name, self.name))

    def write(self, vals):
        self.ensure_one()
        inventory = request.env.ref('equipment_process.inventory_master')

        if 'employee_id' in vals and self.state == 'returned' and vals['employee_id'] == inventory.id:
            self.env['mail.followers'].search(
                [('res_model', '=', 'maintenance.equipment'), ('res_id', '=', self.id),
                 ('partner_id', '=', self.employee_id.user_id.partner_id.id)]).unlink()
            self.message_post(body="Equipment has been transferred to %s" % (inventory.name))
        if 'employee_id' in vals and self.state == 'returned' and vals['employee_id'] != inventory.id:

            self.env['mail.followers'].search(
                [('res_model', '=', 'maintenance.equipment'), ('res_id', '=', self.id),
                 ('partner_id', '=', self.employee_id.user_id.partner_id.id)]).unlink()
            self.message_post(body="Equipment has been transferred to %s, waiting for %s to approve" % (
                self.env['hr.employee'].search([('id', '=', vals['employee_id'])]).name,
                self.env['hr.employee'].search([('id', '=', vals['employee_id'])]).name))
        if 'employee_id' in vals and self.state == 'unapproved' and vals['employee_id'] != inventory.id:
            post_vars = {'subject': "Maintenance Equipment",
                         'partner_ids': [self.env['hr.employee'].browse(vals['employee_id']).user_id.partner_id.id], }
            # Send messages to previous users
            self.message_post(body="%s has been transferred to %s" % (
                self.name, self.env['hr.employee'].browse(vals['employee_id']).name))
            self.message_post(
                body="%s has been transferred to %s" % (
                    self.name, self.env['hr.employee'].browse(vals['employee_id']).name),
                type="notification",
                subtype="mt_comment",
                **post_vars)
        if 'department_id' in vals and vals['employee_id'] != inventory.id:
            self.env['mail.followers'].search(
                [('res_model', '=', 'maintenance.equipment'), ('res_id', '=', self.id),
                 ('partner_id', '=', self.department_id.manager_id.user_id.partner_id.id)]).unlink()
            self.message_post(body="Equipment has been transferred to %s, waiting for Manager Department to approve" % (
                self.env['hr.department'].search([('id', '=', vals['department_id'])]).name,
            ))
        res = super(MaintenanceEquipment, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        equipment = super(MaintenanceEquipment, self).create(vals)
        if equipment.employee_id.id != False and equipment.department_id.id == False:
            equipment.message_post(body="Equipment has been transferred to employee %s, waiting for %s to approve" % (
                equipment.employee_id.name, equipment.employee_id.name))
        elif equipment.employee_id.id == False and equipment.department_id.id != False:
            equipment.message_post(
                body="Equipment has been transferred to department %s, waiting for Manager Department to approve" % (
                    equipment.department_id.name))
        elif equipment.employee_id.id != False and equipment.department_id.id != False:
            equipment.message_post(
                body="Equipment has been transferred to department %s, employee %s waiting to approve" % (
                    equipment.department_id.name, equipment.employee_id.name))
        return equipment

    def unlink(self):
        if self.state != 'unapproved':
            raise UserError("You can't delete this equipment because it not in company's inventory")
        else:
            super(MaintenanceEquipment, self).unlink()

    # def _track_subtype(self, init_values):
    #     self.ensure_one()
    #     if 'state' in init_values:
    #         return 'equipment_process.eq_stage_changed'
    #     return super(MaintenanceEquipment, self)._track_subtype(init_values)
