# AI-Generated/Assisted Code
# Details tracked via `Assisted-by:` trailers in git log
from odoo import fields, models


class LibraryAuthor(models.Model):
    _inherit = 'library.author'

    biography = fields.Text(translate=True)

    def action_book_list(self):
        self.ensure_one()
        return {
            'name': self.env._('Author Books'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'library.book',
            'context': {'default_author_id': self.id},
            'domain': [('author_id', '=', self.id)],
        }
