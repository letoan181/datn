from odoo import models, fields


class ZedeskTicket(models.Model):
    _name = 'zendesk.ticket'

    id = fields.Char('Id')
    name = fields.Char('Name')
    type = fields.Char('Type')
    description = fields.Text('Description')
    priority = fields.Char('Priority')
    created_at = fields.Datetime('Created')
    updated_at = fields.Datetime('Updated')
    status = fields.Char('Status')
    requester_id = fields.Many2one('res.partner', string='Requester')
    assignee_id = fields.Many2one('res.partner', string='Assignee')
    collaborator_ids = fields.Many2many('res.partner')
    conversation_ids = fields.One2many('zendesk.conversation', 'ticket_id')
