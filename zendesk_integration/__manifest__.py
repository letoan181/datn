# -*- coding: utf-8 -*-
{
    'name': "Zendesk Integration",
    'summary': """
        Zendesk Integration""",
    'description': """
        Zendesk Integration
    """,
    'author': "Magenest",
    'website': "http://store.magenest.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'data/zendesk_data.xml',
        'security/ir.model.access.csv',
        'views/tickets_view.xml',
        'views/zendesk_view.xml',
        'views/contact_view.xml',
        'views/conversation_view.xml',
        'views/zendesk_menu.xml',
    ],
}
