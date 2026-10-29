from odoo import http
from odoo.http import request


class OSLController(http.Controller):

    # Сторінка "Мої книги" для будь-якого користувача з логіном.
    # Її відкриває HttpCase з tests/test_http.py
    @http.route('/library/my-books', type='http', auth='user', methods=['GET'])
    def my_books(self):
        partner = request.env.user.partner_id
        # Читач може не мати жодної групи бібліотеки, тобто й прав на модель
        # книги. sudo() тут безпечний: домен обмежує вибірку книгами самого
        # користувача, до шаблону потрапляють лише назва, автор та дата
        books = request.env['odoo.school.library.book'].sudo().search([('reader_id', '=', partner.id)])
        return request.render('odoo_school_library.odoo_school_library_my_books_page', {
            'reader': partner,
            'books': books,
        })
