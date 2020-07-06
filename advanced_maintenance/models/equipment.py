# -*- coding: utf-8 -*-

from odoo import fields, models


class MaintenanceEquipmentTag(models.Model):
    _name = 'maintenance.equipment.tag'
    name = fields.Char(string='Name', required=True)


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    equipment_tags = fields.Many2many(
        'maintenance.equipment.tag', 'maintenance_equipment_tag_rel',
        'equipment_id', 'equipment_tag_id',
        string='Tags', required=True)
    equipment_location = fields.Many2one("expense.location", String="Location", required=True)
