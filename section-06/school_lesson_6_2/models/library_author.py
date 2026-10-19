# AI-Generated/Assisted Code
# Details tracked via `Assisted-by:` trailers in git log
from odoo import api, fields, models


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Library Book Authors'
    _rec_names_search = ['first_name', 'last_name']

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    birth_date = fields.Date(string='Birthday')

    @api.depends('first_name', 'last_name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'{rec.first_name} {rec.last_name}'

    def action_delete(self):
        self.ensure_one()
        self.check_access('unlink')
        self.unlink()

    def _create_by_user(self, vals):
        # sudo() bypasses access rights and record rules: use it only
        # when the business logic must create a record on behalf of
        # a user who has no create permission on the model.
        return self.sudo().create(vals)
