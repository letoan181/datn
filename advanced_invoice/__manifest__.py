# -*- coding: utf-8 -*-
{
    'name': "Advanced Invoice",
    'summary': """
        Pre select payment when create invoice""",

    'description': """
        Pre select payment when create invoice
    """,

    'author': "Magenest",
    'website': "https://store.magenest.com",
    'category': 'Invoicing Management',
    'version': '0.1',
    'depends': ['base', 'sale', 'account', 'crm'],
    'data': [
        'views/account_move_line_onboarding_templates.xml',
        'data/bank_fee_product.xml',
        'security/invoice_security.xml',
        'views/advanced_invoice_views.xml',
        'views/advanced_sale_views.xml',
        'views/advanced_account_payment_view.xml',
        'views/advanced_account_journal_dashboard_view.xml',
        'views/advanced_account_view.xml',
        'views/advanced_crm_lead.xml',
        'views/advanced_expense.xml',
        'views/advanced_bill_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
