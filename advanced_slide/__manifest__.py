# -*- coding: utf-8 -*-
{
    'name': "Advanced Website Slide",

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
    'depends': ['base', 'website_slides', 'survey'],
    'data': [
        'security/ir.model.access.csv',
        'views/survey_template.xml',
        'views/slide_question_import.xml',
        'views/survey_question_view.xml',
        'views/survey_user_input_view.xml',
        'views/question_answer_view.xml',
        'views/teamplate_thank_for_your_submit.xml',
        'wizard/text_answer_detail_view.xml',
    ],
    # 'qweb': ['static/src/xml/survey_header.xml'],
}