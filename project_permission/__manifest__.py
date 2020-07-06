# -*- coding: utf-8 -*-
{
    'name': "Project Permissions",

    'summary': """
        This module sets permissions for some actions in project.""",

    'description': """
        This module sets permissions for some actions in project.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/user_types_view.xml',
        'views/add_followers_view.xml',
        'views/remove_followers_view.xml',
    ],
}
