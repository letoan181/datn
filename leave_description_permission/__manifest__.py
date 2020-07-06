# -*- coding: utf-8 -*-
{
    'name': "Leave Description Permission",

    'summary': """
        This is Leave Description Permission""",

    'description': """
        This is Leave Description Permission
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'resource', 'hr', 'company_location', 'hr_holidays'],

    'data': [
        'views/leave_active_views.xml',
        'security/fix_hr_leave_process_group.xml',
        'security/ir.model.access.csv',
        'views/leave_description_permission_views.xml',
    ],
}
