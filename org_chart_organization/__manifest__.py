# -*- coding: utf-8 -*-
{
    'name': "Organization Chart Department",
    'summary': """Dynamic display of your Department Organization""",
    'description': """Dynamic display of your Department Organization""",
    'author': "SLife Organization, Amichia Fréjus Arnaud AKA",
    'category': 'Human Resources',
    'version': '2.0',
    'license': 'AGPL-3',
    'depends': ['base', 'hr', 'web', 'website'],
    'images': [
        'static/src/img/main_screenshot.png'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/chart_views.xml',
        'views/chart_views_v2.xml',
    ],
    'qweb': [
        # "static/src/xml/org_chart_department.xml",
        # "static/src/xml/org_chart_employee.xml",
        "static/src/xml/org_chart_department_v2.xml",
        "static/src/xml/org_chart_employee_v2.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
