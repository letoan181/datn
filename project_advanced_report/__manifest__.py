# -*- coding: utf-8 -*-
{
    'name': "project_advanced_report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'project_enterprise', 'hr_timesheet', 'web_timeline', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/cron_job_project_task.xml',
        'data/cron_job_unsubcribe.xml',
        'security/project_security.xml',
        'views/views.xml',
        'views/project_views.xml',
        'views/project_report_view.xml',
        'views/qa_person_project_task.xml',
        'views/project_task.xml',
        'views/project_task_timeline_menu.xml',
        'views/project_task_report_calendar_view.xml',
        'views/project_task_report_gantt_view.xml',
        'views/project_task_action.xml',
        'views/project_deadline_view.xml',
        'views/project_filter_invite_employee.xml',
        'views/report_task_miss_deadline.xml',
        'views/project_task_type.xml',
        'wizard/report_miss_deadline_popup.xml',
    ],
    # only loaded in demonstration mode

}
