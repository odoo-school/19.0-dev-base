from dateutil.relativedelta import relativedelta

from odoo import Command, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import LazyTranslate

# Лінивий переклад: рядок оголошено при імпорті файлу, коли мови ще немає,
# перекладається ж він лише при показі користувачу. Змінна має називатися
# саме _lt - екстрактор термінів шукає в коді лише _ та _lt
_lt = LazyTranslate(__name__)

ISSUE_ERRORS = {
    'no_reader': _lt("Set a reader before issuing the book."),
    'no_rights': _lt("Only library staff can issue books."),
}

# Типи активностей, які може створити cron ювілеїв видання
ANNIVERSARY_ACTIVITY_TYPES = {
    'todo': 'mail.mail_activity_data_todo',
    'meeting': 'mail.mail_activity_data_meeting',
}


class OSLBook(models.Model):
    """A book of the library catalogue.

    Each book gets an inventory number from the ``odoo.school.library.book``
    sequence, can be issued to a reader and written off by a library
    administrator. The chatter keeps the history and the activities of a book.
    """

    _name = 'odoo.school.library.book'
    # image.mixin додає поля image_1920, image_1024 ... image_128,
    # mail.thread та mail.activity.mixin - чаттер та активності на формі
    _inherit = ['image.mixin', 'mail.thread', 'mail.activity.mixin']
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

    def action_assign_to_me(self):
        """Make the current user responsible for the books.

        :raises AccessError: if the user is not allowed to modify any of the books
        """
        # check_access: AccessError, якщо змінювати хоч одну книгу
        # з набору заборонено правами доступу чи правилами записів
        self.check_access('write')
        self.write({'user_id': self.env.user.id})

    def action_take_book(self):
        """Issue the books to their readers.

        Only library staff can issue books, and every book must have a reader.
        The books become "Pending" and the readers get the "Reader" tag.

        :raises UserError: if the user is not library staff or a book has no reader
        :raises AccessError: if the user is not allowed to modify the books
        """
        # has_groups: кілька груп через кому, "!" - користувач поза групою
        if not self.env.user.has_groups(
            'odoo_school_library.odoo_school_library_group_user,!base.group_portal'
        ):
            self._raise_issue_error('no_rights')
        if self.filtered(lambda book: not book.reader_id):
            self._raise_issue_error('no_reader')
        # спершу явна перевірка: далі код працює через sudo()
        self.check_access('write')
        self._register_issue()

    def _raise_issue_error(self, code):
        # переклад станеться тут, мовою поточного користувача:
        # self.env._() приймає лінивий рядок так само, як звичайний
        raise UserError(self.env._(ISSUE_ERRORS[code]))

    def _register_issue(self):
        # Приватний метод (префікс _) недоступний з кнопок та RPC.
        # sudo() вимикає перевірки ORM, але self.env.user лишається тим самим
        self.sudo().write({'inventory_state': 'pending'})
        for book in self.filtered(lambda b: not b.taken_date):
            book.sudo().taken_date = fields.Datetime.now()
        # бібліотекар має лише читання res.partner, тож тег "Reader"
        # ставимо через sudo(); тег могли видалити - raise_if_not_found=False
        reader_tag = self.env.ref('odoo_school_library.osl_partner_category_reader', raise_if_not_found=False)
        if reader_tag:
            self.reader_id.sudo().write({'category_id': [Command.link(reader_tag.id)]})

    def action_write_off(self):
        """Write off the books: mark them "Out of stock" and archive them.

        :raises UserError: if the user is not a library administrator
        """
        # has_group: кнопку бачать всі, проте виконати дію може лише адміністратор.
        # self.env._(): рядок перекладається мовою середовища в момент виклику
        if not self.env.user.has_group('odoo_school_library.odoo_school_library_group_manager'):
            raise UserError(self.env._("Only library administrators can write off books."))
        self.write({
            'inventory_state': 'out_of_stock',
            'active': False,
        })

    @api.model
    def _cron_notify_publication_anniversary(self, notify_type='todo', years_step=25):
        """Schedule activities for the books with a publication anniversary this month.

        A book has an anniversary when the number of full years since its
        publication is a multiple of ``years_step`` and it was published in the
        current month. The activity is assigned to the responsible of the book,
        or to the administrator when the book has no responsible.

        :param str notify_type: type of the activity to schedule,
            ``'todo'`` (To-Do) or ``'meeting'`` (Meeting)
        :param int years_step: anniversary step in years, e.g. 25 for
            the 25th, 50th, 75th... anniversaries
        :return: the books an activity was scheduled for
        :rtype: odoo.school.library.book recordset
        :raises ValueError: if ``notify_type`` is unknown
        """
        if notify_type not in ANNIVERSARY_ACTIVITY_TYPES:
            raise ValueError(f"Unknown activity type: {notify_type}")
        today = fields.Date.context_today(self)
        admin = self.env.ref('base.user_admin', raise_if_not_found=False)
        books = self.browse()
        for book in self.search([('publication_date', '!=', False)]):
            years = book._get_publication_age(today)
            if years <= 0 or years % years_step or book.publication_date.month != today.month:
                continue
            books |= book
            book.activity_schedule(
                act_type_xmlid=ANNIVERSARY_ACTIVITY_TYPES[notify_type],
                # relativedelta замість date(рік, місяць, день): для 29 лютого
                # в невисокосний рік він поверне 28 лютого замість помилки
                date_deadline=book.publication_date + relativedelta(years=years),
                summary=self.env._("%(years)s years since publication", years=years),
                user_id=(book.user_id or admin or self.env.user).id,
            )
        return books

    def _get_publication_age(self, on_date):
        """Return the number of calendar years between the publication and ``on_date``.

        :param datetime.date on_date: the date to count the years to
        :rtype: int
        """
        self.ensure_one()
        return on_date.year - self.publication_date.year
