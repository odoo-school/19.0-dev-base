{
    'name': 'Odoo School Library',
    'summary': '',
    'author': 'Odoo School',
    'sequence': -99999999,
    'website': 'https://odoo.school/',
    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '19.0.6.5.0',

    # web - заради шаблону web.frontend_layout на сторінці /library/my-books,
    # mail - чаттер і активності на книзі
    'depends': [
        'base',
        'mail',
        'web',
    ],

    'external_dependencies': {
        'python': [],
    },

    # Master data: завантажуються при кожному встановленні та оновленні.
    # Порядок має значення: групи -> права (CSV посилається на групи)
    # -> правила (посилаються на групи й модель) -> data -> views.
    'data': [
        'security/odoo_school_library_groups.xml',
        'security/ir.model.access.csv',
        'security/odoo_school_library_book_security.xml',

        'data/ir_sequence_data.xml',
        'data/res_partner_category_data.xml',
        'data/ir_cron_data.xml',

        'views/odoo_school_library_menu.xml',
        'views/odoo_school_library_book_views.xml',
        'views/odoo_school_library_config_views.xml',
        'views/odoo_school_library_templates.xml',
    ],

    # Демо-дані: лише в демо-базі (--with-demo) і завжди після data.
    # Автори раніше за книги, XML раніше за CSV, що на нього посилається.
    'demo': [
        'demo/res_partner_demo.xml',
        'demo/res_users_demo.xml',
        'demo/res_company_demo.xml',
        'demo/odoo_school_library_book_demo.xml',
        'demo/odoo.school.library.book.csv',
        'demo/odoo.school.library.book-extra.csv',
    ],

    'installable': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png',
    ],

}
