# AI-Generated/Assisted Code
# Details tracked via `Assisted-by:` trailers in git log
from datetime import date

from odoo import api, fields, models


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _inherit = ['library.author', 'mail.thread', 'mail.activity.mixin']

    @api.model
    def calculate_author_anniversary(self, notify_type: str = 'todo') -> None:
        """Determine author anniversaries for the current month.
        If the anniversary is in the current month an activity will be created.

        :param notify_type: can have two value todo or meeting, determine which activity type to create.
        :return None:
        """
        activity_types = {
            'todo': 'mail.mail_activity_data_todo',
            'meeting': 'mail.mail_activity_data_meeting',
        }
        if notify_type not in activity_types:
            return
        today = fields.Date.today()
        authors = self.env['library.author'].search([('birth_date', '!=', False)])
        for author in authors:
            # Get only those authors whose century anniversary
            # is in the current month
            years = today.year - author.birth_date.year
            if years and years % 100 == 0 and today.month == author.birth_date.month:
                author.activity_schedule(
                    act_type_xmlid=activity_types[notify_type],
                    date_deadline=date(today.year, author.birth_date.month, author.birth_date.day),
                    summary=self.env._("%s anniversary is coming soon.", author.display_name),
                    user_id=self.env.ref('base.user_admin').id,
                )

    def get_bk_cnt(self):
        """This sample method shows a BAD approach for naming."""
        self.ensure_one()
        bc = self.env['library.book'].search_count([
            ('author_id', '=', self.id)])
        return bc

    def get_book_count(self):
        """This sample method shows GOOD approach for naming."""
        self.ensure_one()
        book_count = self.env['library.book'].search_count([
            ('author_id', '=', self.id)])
        return book_count
