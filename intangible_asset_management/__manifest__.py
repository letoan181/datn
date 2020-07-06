{
    'name': "Intangible Assets Management",
    'summary': """
        An app to manage intangible assets""",
    'description': """
        Created by Magenest
    """,
    'author': "Magenest JSC",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr', 'portal', 'mail', 'rating', 'hr_maintenance'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/intangible_asset_view.xml',
        'views/hr_employee_view.xml',
        'demo/demo.xml',
    ],
}