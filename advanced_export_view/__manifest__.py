# -*- coding: utf-8 -*-
{
    'name': 'Export Current View',
    'version': '1.0.0.0',
    'category': 'Web',
    'author': 'My Company',
    'website': 'store.magenest.com',
    'depends': [
        'web',
    ],
    "data": [
        'views/advanced_export_view_view.xml',
    ],
    'qweb': [
        "static/src/xml/advanced_export_view_template.xml",
    ],
    'installable': True,
    'auto_install': False,
}
