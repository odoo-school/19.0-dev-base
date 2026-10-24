from odoo.exceptions import UserError
from odoo.tests import TransactionCase, new_test_user, tagged


# Терміни коду читаються прямо з i18n/uk.po, тож мову достатньо
# активувати - завантажувати переклади в базу для цього не потрібно
@tagged('post_install', '-at_install')
class TestLibraryTranslations(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.lang']._activate_lang('uk_UA')
        cls.librarian = new_test_user(
            cls.env, login='test_librarian_uk',
            groups='odoo_school_library.odoo_school_library_group_user',
        )
        # внутрішній користувач без групи бібліотеки
        cls.employee = new_test_user(cls.env, login='test_employee_uk', groups='base.group_user')
        cls.book = cls.env['odoo.school.library.book'].create({
            'name': 'Kobzar', 'user_id': cls.librarian.id,
        })

    def test_write_off_error_is_translated(self):
        book = self.book.with_user(self.librarian).with_context(lang='uk_UA')
        with self.assertRaisesRegex(UserError, 'Списувати книги можуть лише адміністратори бібліотеки.'):
            book.action_write_off()

    def test_lazy_no_reader_error_is_translated(self):
        # лінивий рядок з ISSUE_ERRORS['no_reader']
        book = self.book.with_user(self.librarian).with_context(lang='uk_UA')
        with self.assertRaisesRegex(UserError, 'Перед видачею книги вкажіть читача.'):
            book.action_take_book()

    def test_lazy_no_rights_error_is_translated(self):
        # лінивий рядок з ISSUE_ERRORS['no_rights']
        book = self.book.with_user(self.employee).with_context(lang='uk_UA')
        with self.assertRaisesRegex(UserError, 'Видавати книги можуть лише працівники бібліотеки.'):
            book.action_take_book()

    def test_english_source_without_lang(self):
        book = self.book.with_user(self.librarian).with_context(lang='en_US')
        with self.assertRaisesRegex(UserError, 'Only library administrators can write off books.'):
            book.action_write_off()
