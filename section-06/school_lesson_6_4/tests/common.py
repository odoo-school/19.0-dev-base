# AI-Generated/Assisted Code
# Details tracked via `Assisted-by:` trailers in git log
from odoo import Command
from odoo.tests import TransactionCase


class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_library_user = cls.env.ref(
            'school_lesson_6_2.group_library_user')
        cls.group_library_admin = cls.env.ref(
            'school_lesson_6_2.group_library_admin')
        cls.library_user = cls.env['res.users'].create({
            'name': 'Library User',
            'login': 'library_user',
            'group_ids': [Command.link(cls.env.ref('base.group_user').id),
                          Command.link(cls.group_library_user.id)],
        })
        cls.library_admin = cls.env['res.users'].create({
            'name': 'Library Admin',
            'login': 'library_admin',
            'group_ids': [Command.link(cls.env.ref('base.group_user').id),
                          Command.link(cls.group_library_admin.id)],
        })
        cls.reader = cls.env['res.partner'].create({'name': 'Demo Reader'})
        cls.book_demo = cls.env['library.book'].create({
            'name': 'Demo Book'})
