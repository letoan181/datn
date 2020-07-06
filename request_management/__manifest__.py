# -*- coding: utf-8 -*-
{
    'name': "Request Management",

    'summary': """
        This module request management""",

    'description': """
        This module request management
    """,

    'author': "Magenest",
    'website': "https://store.magenest.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'mail', 'hr'],

    'data': [
        'data/data.xml',
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/menu.xml',
        'views/search_filter.xml',
    ],
}
