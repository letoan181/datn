# -*- coding: utf-8 -*-
{
    'name': "Equipment Process",

    'summary': """An app to manage process equipment
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Magenest",
    'website': "http://www.yourcompany.com",
    'category': 'Maintenance Equipment',
    'version': '0.1',

    'depends': ['base', 'maintenance', 'hr_maintenance', 'hr'],

    'data': [
        'views/maintenance_equipment_view.xml',
        'views/hr_employee_view.xml',
        'security/group.xml',
        'demo/demo.xml',
        'security/ir.model.access.csv',
    ],
}
