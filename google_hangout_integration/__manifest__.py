# -*- coding: utf-8 -*-
{
    'name': "Advanced Document Management",
    'summary': """
        Easy manage document with google drive""",
    'description': """
        Advanced Document Management
        =======================================
        Notes:
        
        
        + Follow this guide to install google python lib 
        
        pip install --upgrade google-api-python-client oauth2client
        
        https://developers.google.com/drive/api/v3/quickstart/python
        
    """,
    'author': "Magenest",
    'website': "https://store.magenest.com/",
    'category': 'Extra Tools',
    'version': '0.1',
    'depends': ['base', 'project', 'sale_management', 'google_drive', 'web'],
    'data': [
        'data/document_security.xml',
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/menu_document.xml',
        'views/view_document_general.xml',
        'views/view_document_file_permission.xml',
        'views/view_document_file_permission_error.xml',
        'views/view_document_permission.xml',
        'views/view_document_general_file.xml',
        'views/view_document_project_file.xml',
        'views/view_document_quotation_file.xml',
        'views/res_config_settings.xml',
        'views/quotation_document.xml',
        'views/project_document.xml',
        'views/view_setting_document.xml',
        'data/mass_sync_user_permission.xml',
        'views/list_editable_renderer_inherit_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
