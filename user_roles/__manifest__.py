# -*- coding: utf-8 -*-
{
    'name': "UserRole",
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
    'depends': ['base'],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/user_roles_change_password.xml',
        'views/user_role_view.xml',
        'views/inherit_user.xml',
    ],
    'demo': [
    ],
}
