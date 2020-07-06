from odoo import models, fields


class ZendeskContact(models.Model):
    _inherit = 'res.partner'

    zendesk_id = fields.Char(string='Zendesk Id')
    zendesk_role = fields.Char(string='Zendesk Role')
    request_ticket = fields.One2many('zendesk.ticket', 'requester_id', string='Request Ticket')
    assign_ticket = fields.One2many('zendesk.ticket', 'assignee_id', string='Assign Ticket')
    collaborate_ticket = fields.Many2many('zendesk.ticket', string='Collaborate Ticket')
    zendesk_created_at = fields.Datetime('Created')
