from datetime import date

from odoo.tests import freeze_time, tagged

from .common import OSLTestCommon


@tagged('post_install', '-at_install', 'osl')
@freeze_time('2026-03-01')
class TestOSLPublicationAnniversary(OSLTestCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.jubilee_book = cls.Book.create({
            'name': 'Jubilee Book', 'publication_date': date(1926, 3, 15), 'user_id': cls.librarian.id,
        })
        cls.other_year_book = cls.Book.create({'name': 'Other Year', 'publication_date': date(1927, 3, 15)})
        cls.other_month_book = cls.Book.create({'name': 'Other Month', 'publication_date': date(1926, 4, 15)})
        cls.no_date_book = cls.Book.create({'name': 'No Date'})

    def test_activity_for_anniversary_this_month(self):
        books = self.Book._cron_notify_publication_anniversary()
        self.assertIn(self.jubilee_book, books)
        self.assertNotIn(self.other_year_book, books)
        self.assertNotIn(self.other_month_book, books)
        self.assertNotIn(self.no_date_book, books)

        activity = self.jubilee_book.activity_ids
        self.assertEqual(len(activity), 1)
        self.assertEqual(activity.user_id, self.librarian, 'The responsible of the book gets the activity')
        self.assertEqual(activity.date_deadline, date(2026, 3, 15))
        self.assertEqual(activity.activity_type_id, self.env.ref('mail.mail_activity_data_todo'))

    def test_years_step(self):
        # 99 років - не кратне 25, але кратне 33
        book = self.Book.create({'name': '99 Years', 'publication_date': date(1927, 3, 1)})
        self.assertNotIn(book, self.Book._cron_notify_publication_anniversary())
        self.assertIn(book, self.Book._cron_notify_publication_anniversary(years_step=33))

    def test_meeting_activity_type(self):
        self.Book._cron_notify_publication_anniversary(notify_type='meeting')
        self.assertEqual(self.jubilee_book.activity_ids.activity_type_id,
                         self.env.ref('mail.mail_activity_data_meeting'))

    def test_unknown_activity_type(self):
        with self.assertRaises(ValueError):
            self.Book._cron_notify_publication_anniversary(notify_type='call')
