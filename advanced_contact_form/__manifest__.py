# -*- coding: utf-8 -*-
{
    'name': "advanced_contact_form",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'crm'],
    'data': [
        'views/crm_lead.xml',
        'data/mail_template.xml',
    ],
}
