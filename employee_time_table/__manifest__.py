# -*- coding: utf-8 -*-
{
    'name': "Employee Time Table",

    'summary': """
        Employee Time Table
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'calendar', 'hr_timesheet','website'],

    # always loaded
    'data': [
        'views/group.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [
        "/static/xml/time_table_employee.xml",
    ],
}
