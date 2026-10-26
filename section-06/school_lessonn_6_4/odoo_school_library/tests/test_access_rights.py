from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import OSLTestCommon


# Перевірки робимо від імені користувача через with_user. Книги створює
# суперкористувач (cls.env), тож на демо-дані тести не спираються.
# Числовий префікс в назвах методів задає порядок їх виконання
@tagged('post_install', '-at_install', 'osl', 'osl_access')
class TestOSLAccessRights(OSLTestCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.own_book = cls.Book.create({'name': 'Own Book', 'user_id': cls.librarian.id})
        cls.foreign_book = cls.Book.create({'name': 'Foreign Book', 'user_id': cls.other_librarian.id})
        cls.free_book = cls.Book.create({'name': 'Unassigned Book'})
        cls.all_books = cls.own_book | cls.foreign_book | cls.free_book

    def test_01_librarian_access_rights(self):
        books = self.Book.with_user(self.librarian).search([])
        self.assertIn(self.own_book, books)
        self.assertIn(self.free_book, books)
        self.assertNotIn(self.foreign_book, books)
        with self.assertRaises(AccessError):
            self.own_book.with_user(self.librarian).unlink()

    def test_02_library_admin_access_rights(self):
        books = self.Book.with_user(self.manager).search([])
        self.assertEqual(books & self.all_books, self.all_books)
        book = self.Book.with_user(self.manager).create({'name': 'Test Book'})
        book.write({'name': 'Test Book II'})
        book.unlink()

    def test_03_employee_has_no_access(self):
        with self.assertRaises(AccessError):
            self.Book.with_user(self.employee).search([])

    def test_has_access_and_filtered_access(self):
        books = self.all_books.with_user(self.librarian)
        # has_access повертає True/False замість винятку
        self.assertTrue(self.own_book.with_user(self.librarian).has_access('write'))
        self.assertFalse(self.foreign_book.with_user(self.librarian).has_access('write'))
        self.assertFalse(self.own_book.with_user(self.librarian).has_access('unlink'))
        # _filtered_access залишає лише записи, для яких операція дозволена
        self.assertEqual(books._filtered_access('write'), (self.own_book | self.free_book).with_user(self.librarian))

    def test_assign_to_me(self):
        self.free_book.with_user(self.librarian).action_assign_to_me()
        self.assertEqual(self.free_book.user_id, self.librarian)
        with self.assertRaises(AccessError):
            self.foreign_book.with_user(self.librarian).action_assign_to_me()

    def test_take_book_works_through_sudo(self):
        self.own_book.reader_id = self.reader
        self.reader.category_id = False
        self.own_book.with_user(self.librarian).action_take_book()
        self.assertEqual(self.own_book.inventory_state, 'pending')
        # sudo() не змінює користувача: автор змін - бібліотекар
        self.assertEqual(self.own_book.write_uid, self.librarian)
        reader_tag = self.env.ref('odoo_school_library.osl_partner_category_reader', raise_if_not_found=False)
        if reader_tag:
            self.assertIn(reader_tag, self.reader.category_id)
            self.assertEqual(self.reader.write_uid, self.librarian)

    def test_create_uid_is_librarian(self):
        book = self.Book.with_user(self.librarian).create({'name': 'New Book'})
        self.assertEqual(book.create_uid, self.librarian)

    def test_purchase_price_hidden_from_librarian(self):
        with self.assertRaises(AccessError):
            self.own_book.with_user(self.librarian).read(['purchase_price'])
        self.own_book.with_user(self.manager).read(['purchase_price'])
