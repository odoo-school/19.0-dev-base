# AI-Generated/Assisted Code
# Details tracked via `Assisted-by:` trailers in git log
from datetime import date

from odoo import fields
from odoo.tests import Form, freeze_time, tagged

from odoo.addons.school_lesson_6_4.tests.common import TestCommon


@tagged('post_install', '-at_install', 'library')
class TestForm(TestCommon):

    @freeze_time('2026-01-15')
    def test_book_taken_date(self):
        # Assigning a reader sets the "In use from" date to today
        book_form = Form(self.book_demo)
        book_form.reader_id = self.library_user.partner_id
        self.assertEqual(book_form.taken_date, date(2026, 1, 15))

        # Changing the reader keeps the already set date
        yesterday = date(2026, 1, 14)
        self.book_demo.write({'taken_date': yesterday, 'reader_id': False})
        book_form = Form(self.book_demo)
        book_form.reader_id = self.reader
        self.assertEqual(fields.Date.to_date(book_form.taken_date), yesterday)
