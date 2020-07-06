# -*- coding: utf-8 -*-
{
    'name': "user_lock",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'auth_signup', 'hr', 'project_advanced_report'],
    'data': [
        'views/additional_res_users_views.xml',
        'views/res_users_view_form_profile_inherit.xml'
    ],
}
