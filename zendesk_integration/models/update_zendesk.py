from ..lib.zendesk_api import ZendeskGet

from odoo import models, fields, api


class UpdateZendesk(models.Model):
    _name = 'zendesk.update'
    name = fields.Char('Name')
    zendesk_domain = fields.Char('Domain', help='example: me.zendesk.com')
    zendesk_username = fields.Char('Username')
    zendesk_api_token = fields.Char('Api Token')
    last_update_user_time = fields.Char('Last update user time', default='2019-01-01')
    last_update_ticket_time = fields.Char('Last update ticket time', default='2019-01-01')

    def update_zendesk(self):
        if self.zendesk_domain and self.zendesk_username and self.zendesk_api_token:
            current_field = self.env['zendesk.update'].search([], limit=1)
            current_field.update_contact()
        else:
            return

    def update_contact(self):
        zendesk = ZendeskGet(self.zendesk_domain, self.zendesk_username, self.zendesk_api_token)
        res = zendesk.get_user_after_time(self.last_update_user_time)
        if res['count'] > 0:
            for user in res['results']:
                if user['email'] != None:
                    self.env['res.partner'].create({
                        'name': user['name'],
                        'email': user['email'],
                        'phone': user['phone'],
                        'zendesk_id': user['id'],
                        'zendesk_role': user['role'],
                        'zendesk_created_at': user['created_at']
                    })
            self.last_update_user_time = str(res['results'][0]['created_at'])
        self.update_ticket()

    def update_ticket(self):
        zendesk = ZendeskGet(self.zendesk_domain, self.zendesk_username, self.zendesk_api_token)
        res = zendesk.get_ticket_after_time(self.last_update_ticket_time)
        if res['count'] > 0:
            for ticket in res['results']:
                self.env['zendesk.ticket'].create({
                    'name': 'Ticket %s' % ticket['id'],
                    'type': ticket['type'],
                    'description': ticket['description'],
                    'priority': ticket['priority'],
                    'created_at': ticket['created_at'],
                    'updated_at': ticket['updated_at'],
                    'status': ticket['status'],
                    'requester_id': self.search_partner([ticket['requester_id']]),
                    'assignee_id': self.search_partner([ticket['assignee_id']]),
                    'collaborator_ids': self.search_partner(ticket['collaborator_ids'])
                })
                self.update_comment(str(ticket['id']))
            self.last_update_ticket_time = res['results'][0]['created_at']

    def search_partner(self, zendesk_id):
        partner = self.env['res.partner'].search([('zendesk_id', 'in', zendesk_id)])
        return partner.id

    def update_comment(self, ticket_id):
        zendesk = ZendeskGet(self.zendesk_domain, self.zendesk_username, self.zendesk_api_token)
        res = zendesk.get_comment_of_ticket(ticket_id)
        for comment in res['comments']:
            self.env['zendesk.conversation'].create({
                'name': comment['id'],
                'body': comment['html_body'],
                'created_at': comment['created_at'],
                'ticket_id': self.search_ticket('Ticket ' + ticket_id)
            })

    def search_ticket(self, ticket_name):
        ticket = self.env['zendesk.ticket'].search([('name', '=', ticket_name)])
        return ticket.id
