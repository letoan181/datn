# -*- coding: utf-8 -*-
{
    'name': "Advanced_CRM",

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
    'depends': ['base', 'crm', 'sale_crm', 'advanced_contact_form', 'mail', 'project', 'document_management','fetchmail'],
    'data': [
        'security/ir.model.access.csv',
        'data/project_type_data.xml',
        'data/crm_lead_location.xml',
        'data/crm_lead_state.xml',
        'data/mail_template_data.xml',
        'data/lead_ir_cron.xml',
        'data/utm_source_data.xml',
        'data/group.xml',
        'views/menu_config_activity_stage_opportunity.xml',
        'views/crm_lead.xml',
        'views/fetch_mail_view.xml',
        'views/res_partner_inherit.xml',
        'views/hr_employee.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}