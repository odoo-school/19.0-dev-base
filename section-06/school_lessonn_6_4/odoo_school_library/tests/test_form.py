from datetime import datetime

from odoo import fields
from odoo.tests import Form, freeze_time, tagged

from .common import OSLTestCommon


# Form відтворює роботу форми на сервері: default_get при створенні,
# onchange при кожній зміні поля, save() - запис до бази
@tagged('post_install', '-at_install', 'osl')
class TestOSLForm(OSLTestCommon):

    # freeze_time "зупиняє" час, тож Datetime.now() в коді завжди однаковий
    @freeze_time('2026-01-15 10:00:00')
    def test_taken_date_set_on_reader(self):
        book_form = Form(self.Book)
        book_form.name = 'Test Book'
        self.assertFalse(book_form.taken_date)
        book_form.reader_id = self.reader
        self.assertEqual(book_form.taken_date, datetime(2026, 1, 15, 10, 0))
        book = book_form.save()
        self.assertEqual(book.taken_date, datetime(2026, 1, 15, 10, 0),
                         'taken_date is readonly but force_save must store it')

    @freeze_time('2026-01-15 10:00:00')
    def test_taken_date_kept_on_reader_change(self):
        taken_date = datetime(2026, 1, 10, 9, 0)
        book = self.Book.create({'name': 'Test Book', 'reader_id': self.reader.id, 'taken_date': taken_date})
        book_form = Form(book)
        book_form.reader_id = self.author
        # значення, яке onchange не змінив, Form тримає рядком, як його віддає сервер
        self.assertEqual(fields.Datetime.to_datetime(book_form.taken_date), taken_date)

    def test_default_inventory_state(self):
        book_form = Form(self.Book)
        self.assertEqual(book_form.inventory_state, 'available')
