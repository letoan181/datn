from odoo import models, fields


class ZendeskConversation(models.Model):
    _name = 'zendesk.conversation'

    id = fields.Char('Id')
    name = fields.Char('Name')
    body = fields.Html('Body')
    created_at = fields.Datetime('Created')
    ticket_id = fields.Many2one('zendesk.ticket', string='Ticket')
