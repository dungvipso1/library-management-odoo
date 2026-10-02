{
    'name': 'Library Management',
    'version': '1.0.0',
    'category': 'Services',
    'summary': 'Hệ thống quản lý thư viện',
    'description': """
        Hệ thống quản lý thư viện được xây dựng
        trên nền tảng Odoo ERP.
    """,
    'author': 'Sinh viên khóa luận',
    'website': '',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'website',
    ],

    'data': [
        'data/loan_sequence.xml',
        'data/fine_sequence.xml',
        'data/library_cron.xml',
        'data/reservation_sequence.xml',

        'security/library_security.xml',
        'security/ir.model.access.csv',

        'views/library_book_views.xml',
        'views/member_views.xml',
        'views/loan_views.xml',
        'views/fine_views.xml',
        'views/report_views.xml',
        'views/website_templates.xml',
        'views/reservation_views.xml',
        'views/dashboard_templates.xml',
    ],

    'installable': True,
    'application': True,
}