# -*- coding: utf-8 -*-
{
    'name': "Advanced_Contact",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Magenest VietNam",
    'website': "https://store.magenest.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'hr', 'sale', 'account', 'company_location'],

    # always loaded
    'data': [
        'data/remove_inactive_partner_cron.xml',
        'views/res_groups.xml',
        'views/ir_cron.xml',
        'views/res_partner_view.xml',
        'views/hr_employee_view.xml',
        'views/res_users_view.xml',
    ],
}