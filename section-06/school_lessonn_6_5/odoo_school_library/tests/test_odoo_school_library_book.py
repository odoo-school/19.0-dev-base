from psycopg2.errors import UniqueViolation

from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import OSLTestCommon


# Мітка osl - для вибіркового запуску: --test-tags osl
@tagged('post_install', '-at_install', 'osl')
class TestOSLBook(OSLTestCommon):

    def test_master_data_loaded(self):
        # Master data можуть видалити - тому raise_if_not_found=False
        sequence = self.env.ref('odoo_school_library.osl_seq_library_book', raise_if_not_found=False)
        self.assertTrue(sequence, 'The book sequence must be created from data/')
        self.assertEqual(sequence.code, 'odoo.school.library.book')

        author_tag = self.env.ref('odoo_school_library.osl_partner_category_author', raise_if_not_found=False)
        self.assertTrue(author_tag, 'The "Author" partner tag must be created from data/')

    def test_inventory_number_from_sequence(self):
        sequence = self.env['ir.sequence'].search([('code', '=', 'odoo.school.library.book')], limit=1)
        book_1, book_2 = self.Book.create([
            {'name': 'Test Book 1', 'author_id': self.author.id},
            {'name': 'Test Book 2', 'author_id': self.author.id},
        ])
        self.assertTrue(book_1.inventory_number.startswith(sequence.prefix))
        self.assertTrue(book_2.inventory_number.startswith(sequence.prefix))
        self.assertNotEqual(book_1.inventory_number, book_2.inventory_number)

    def test_inventory_number_not_copied(self):
        book = self.Book.create({'name': 'Test Book'})
        book_copy = book.copy()
        self.assertTrue(book_copy.inventory_number)
        self.assertNotEqual(book.inventory_number, book_copy.inventory_number)

    def test_isbn_unique(self):
        self.Book.create({'name': 'Test Book 1', 'isbn': '978-0-00-000000-2'})
        with mute_logger('odoo.sql_db'), self.assertRaises(UniqueViolation):
            self.Book.create({'name': 'Test Book 2', 'isbn': '978-0-00-000000-2'})
