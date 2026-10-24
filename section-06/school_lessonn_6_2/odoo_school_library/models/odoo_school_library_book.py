from odoo import Command, api, fields, models
from odoo.exceptions import UserError


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
    # groups на полі моделі - це вже безпека: поза групою поле
    # прибирається з view, читання через ORM чи RPC дає AccessError
    purchase_price = fields.Float(
        groups='odoo_school_library.odoo_school_library_group_manager',
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

    # check_access: AccessError, якщо змінювати хоч одну книгу
    # з набору заборонено правами доступу чи правилами записів
    def action_assign_to_me(self):
        self.check_access('write')
        self.write({'user_id': self.env.user.id})

    # has_groups: кілька груп через кому, "!" - користувач поза групою
    def action_take_book(self):
        if not self.env.user.has_groups(
            'odoo_school_library.odoo_school_library_group_user,!base.group_portal'
        ):
            raise UserError(self.env._("Only library staff can issue books."))
        if not all(self.mapped('reader_id')):
            raise UserError(self.env._("Set a reader before issuing the book."))
        # спершу явна перевірка: далі код працює через sudo()
        self.check_access('write')
        self._register_issue()

    def _register_issue(self):
        # Приватний метод (префікс _) недоступний з кнопок та RPC.
        # sudo() вимикає перевірки ORM, але self.env.user лишається тим самим
        self.sudo().write({'inventory_state': 'pending'})
        for book in self.filtered(lambda b: not b.taken_date):
            book.sudo().taken_date = fields.Datetime.now()
        # бібліотекар має лише читання res.partner, тож тег "Читач"
        # ставимо через sudo(); тег могли видалити - raise_if_not_found=False
        reader_tag = self.env.ref('odoo_school_library.osl_partner_category_reader', raise_if_not_found=False)
        if reader_tag:
            self.reader_id.sudo().write({'category_id': [Command.link(reader_tag.id)]})

    # has_group: кнопку бачать всі, проте виконати дію може лише адміністратор
    def action_write_off(self):
        if not self.env.user.has_group('odoo_school_library.odoo_school_library_group_manager'):
            raise UserError(self.env._("Only library administrators can write off books."))
        self.write({
            'inventory_state': 'out_of_stock',
            'active': False,
        })
