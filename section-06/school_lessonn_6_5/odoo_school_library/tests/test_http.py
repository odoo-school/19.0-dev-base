from odoo.tests import HttpCase, new_test_user, tagged


# HttpCase піднімає HTTP-сервер в тій самій транзакції, що й тест:
# записи з setUpClass видно в запитах, після тесту ж все відкочується.
# post_install - сторінка має працювати, коли встановлено всі модулі
@tagged('post_install', '-at_install', 'osl', 'osl_http')
class TestOSLMyBooksPage(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # new_test_user задає пароль, що дорівнює логіну.
        # Читачу група бібліотеки не потрібна - лише внутрішній користувач
        cls.reader_user = new_test_user(cls.env, login='test_reader_http', groups='base.group_user')
        Book = cls.env['odoo.school.library.book']
        cls.reader_book = Book.create({
            'name': 'Twenty Thousand Leagues Under the Seas',
            'reader_id': cls.reader_user.partner_id.id,
        })
        cls.other_book = Book.create({'name': 'Another Reader Book'})

    def test_my_books_page(self):
        self.authenticate('test_reader_http', 'test_reader_http')
        response = self.url_open('/library/my-books')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.reader_book.name, response.text, "The reader's book must be listed")
        self.assertNotIn(self.other_book.name, response.text, 'Books of other readers must not be listed')

    def test_my_books_page_requires_login(self):
        response = self.url_open('/library/my-books', allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertIn('/web/login', response.headers['Location'])
