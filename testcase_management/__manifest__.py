# -*- coding: utf-8 -*-
{
    'name': "testcase_management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Magenest",
    'website': "https://store.magenest.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'testcase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'project', 'hr_timesheet', 'mycontract'],

    # always loaded
    'data': [
        'security/testcase_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/testcase.xml',
        'views/templates.xml',
        'views/task_view.xml',
        'views/project_view.xml',
        'wizard/mass_action_change_task_testcase_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        "static/src/xml/testcase_tree_statistic_view.xml",
    ],
}
