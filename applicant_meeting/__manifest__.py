# -*- coding: utf-8 -*-
{
    'name': "Interview_Meeting",

    'summary': """
        This module creates a button in Application's form view to display schedule interview meetings on current applicant,""",

    'description': """
        This module creates a button in Application's form view to display schedule interview meetings on current applicant,
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment', 'calendar'],

    # always loaded
    'data': [
        'views/interview_views.xml',
    ],
}