from odoo import api, fields, models


class OSLBook(models.Model):
    _name = 'odoo.school.library.book'
    # image.mixin додає поля image_1920, image_1024 ... image_128
    _inherit = ['image.mixin']
    _description = 'Book'

    name = fields.Char(
        string='Title',
        required=True,
    )
    isbn = fields.Char(
        string='ISBN',
        copy=False,
    )
    inventory_number = fields.Char(
        readonly=True,
        copy=False,
        help="Assigned automatically from the 'odoo.school.library.book' sequence",
    )
    author_id = fields.Many2one(
        comodel_name='res.partner',
        string='Author',
    )
    publication_date = fields.Date()
    inventory_state = fields.Selection(
        [('available', 'Available'),
         ('pending', 'Pending'),
         ('out_of_stock', 'Out of stock')],
        default='available',
        string='Inventory State',
    )
    reader_id = fields.Many2one(
        comodel_name='res.partner',
        string='Reader',
    )
    taken_date = fields.Datetime(
        string='Taken On',
        readonly=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
    )
    active = fields.Boolean(
        default=True,
    )

    _isbn_uniq = models.Constraint(
        'UNIQUE(isbn)',
        'A book with this ISBN already exists!',
    )

    # Інвентарний номер береться з послідовності, створеної
    # в data/ir_sequence_data.xml (master data)
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('inventory_number'):
                vals['inventory_number'] = self.env['ir.sequence'].next_by_code(
                    'odoo.school.library.book')
        return super().create(vals_list)

    @api.onchange('reader_id')
    def _onchange_reader_id(self):
        if self.reader_id and not self.taken_date:
            self.taken_date = fields.Datetime.now()
