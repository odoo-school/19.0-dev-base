# AI-Generated/Assisted Code
# Details tracked via `Assisted-by:` trailers in git log
from odoo import fields, models


class LibraryBook(models.Model):
    _inherit = 'library.book'

    type = fields.Selection(
        selection=[
            ('brochure', 'Brochure'),
            ('book', 'Book'),
            ('encyclopedia', 'Encyclopedia'),
        ],
        string='Type',
        default='book',
    )
