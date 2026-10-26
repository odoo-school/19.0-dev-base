from odoo.tests import TransactionCase, new_test_user


class OSLTestCommon(TransactionCase):
    """Спільні дані для всіх тестів бібліотеки.

    setUpClass виконується один раз для класу, тож користувачі й партнери
    створюються лише раз, проте кожен тест працює з ними всередині власного
    savepoint. Від демо-даних тести не залежать: все потрібне створюється тут.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Book = cls.env['odoo.school.library.book']

        group_user = 'odoo_school_library.odoo_school_library_group_user'
        group_manager = 'odoo_school_library.odoo_school_library_group_manager'
        cls.librarian = new_test_user(cls.env, login='test_librarian', groups=group_user)
        cls.other_librarian = new_test_user(cls.env, login='test_other_librarian', groups=group_user)
        cls.manager = new_test_user(cls.env, login='test_library_manager', groups=group_manager)
        # внутрішній користувач без жодної групи бібліотеки
        cls.employee = new_test_user(cls.env, login='test_employee', groups='base.group_user')

        cls.author = cls.env['res.partner'].create({'name': 'Test Author'})
        cls.reader = cls.env['res.partner'].create({'name': 'Test Reader'})
