# AI-Generated/Assisted Code
# Details tracked via `Assisted-by:` trailers in git log
from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install', 'library')
class TestLibraryBooksPage(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_password = 'info'
        cls.user = cls.env['res.users'].create({
            'name': 'Library User Http',
            'login': 'library_user_http',
            'password': cls.user_password,
            'group_ids': [
                Command.link(cls.env.ref('base.group_user').id),
                Command.link(cls.env.ref('school_lesson_6_2.group_library_user').id),
            ],
        })
        cls.book = cls.env['library.book'].create({
            'name': 'Twenty Thousand Leagues Under the Seas',
            'reader_id': cls.user.partner_id.id,
        })

    def test_http(self):
        self.authenticate(self.user.login, self.user_password)
        r = self.url_open('/library/books')
        self.assertTrue(r.ok, r.text)
        self.assertIn('Books in use of', r.text, 'Table title must be in the page.')
        self.assertIn(self.book.name, r.text, "The reader's book must be listed.")
