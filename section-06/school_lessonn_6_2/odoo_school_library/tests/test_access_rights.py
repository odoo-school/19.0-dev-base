from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged


# Користувачів створюємо через new_test_user, перевірки робимо
# від їхнього імені через with_user. Записи створює суперкористувач
# (cls.env), тож на демо-дані тести не спираються
@tagged('post_install', '-at_install')
class TestLibraryAccess(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group_user = 'odoo_school_library.odoo_school_library_group_user'
        group_manager = 'odoo_school_library.odoo_school_library_group_manager'
        cls.librarian = new_test_user(cls.env, login='test_librarian', groups=group_user)
        cls.other = new_test_user(cls.env, login='test_other_librarian', groups=group_user)
        cls.manager = new_test_user(cls.env, login='test_library_manager', groups=group_manager)
        cls.reader = cls.env['res.partner'].create({'name': 'Test Reader'})

        Book = cls.env['odoo.school.library.book']
        cls.own_book = Book.create({'name': 'Own Book', 'user_id': cls.librarian.id})
        cls.foreign_book = Book.create({'name': 'Foreign Book', 'user_id': cls.other.id})
        cls.free_book = Book.create({'name': 'Unassigned Book'})
        cls.all_books = cls.own_book | cls.foreign_book | cls.free_book

    def test_librarian_sees_own_and_unassigned_only(self):
        books = self.env['odoo.school.library.book'].with_user(self.librarian).search([])
        self.assertIn(self.own_book, books)
        self.assertIn(self.free_book, books)
        self.assertNotIn(self.foreign_book, books)

    def test_manager_sees_all_books(self):
        books = self.env['odoo.school.library.book'].with_user(self.manager).search([])
        self.assertEqual(books & self.all_books, self.all_books)

    def test_librarian_cannot_delete_book(self):
        with self.assertRaises(AccessError):
            self.own_book.with_user(self.librarian).unlink()

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
        book = self.env['odoo.school.library.book'].with_user(self.librarian).create({'name': 'New Book'})
        self.assertEqual(book.create_uid, self.librarian)

    def test_purchase_price_hidden_from_librarian(self):
        with self.assertRaises(AccessError):
            self.own_book.with_user(self.librarian).read(['purchase_price'])
        self.own_book.with_user(self.manager).read(['purchase_price'])
