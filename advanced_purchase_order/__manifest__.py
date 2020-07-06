# -*- coding: utf-8 -*-
{
    'name': "Advanced Purchase Order",
    'summary': """
        Add group cancel PO
        """,

    'description': """
        Pre select payment when create invoice
    """,

    'author': "Magenest",
    'website': "https://store.magenest.com",
    'category': 'Invoicing Management',
    'version': '0.1',
    'depends': ['base', 'purchase'],
    'data': [
        'data/res_groups.xml',
        'views/purchase_order_form_inherit.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
