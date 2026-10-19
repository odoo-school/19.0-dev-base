# AI-Generated/Assisted Code
# Details tracked via `Assisted-by:` trailers in git log
from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

ERR_MSG = _lt("You can't lend a book in advance.")


class LibraryBook(models.Model):
    _inherit = 'library.book'

    description = fields.Text(translate=True)

    def write(self, vals):
        if vals.get('taken_date') and fields.Date.to_date(vals['taken_date']) > fields.Date.today():
            raise UserError(self.env._(ERR_MSG))
        return super().write(vals)
