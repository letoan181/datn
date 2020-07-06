{
    'name': "Project Default Tags",
    'summary': """
        Add default tags to all tasks in a project""",
    'description': """
        Add default tags to all tasks in a project
    """,
    'author': "Magenest",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project'],

    # always loaded
    'data': [
        'views/project_views.xml',
    ],
}
