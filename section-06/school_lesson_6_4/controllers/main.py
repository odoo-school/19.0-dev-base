# AI-Generated/Assisted Code
# Details tracked via `Assisted-by:` trailers in git log
from odoo import http
from odoo.http import request


class LibraryController(http.Controller):

    @http.route('/library/books', type='http', auth='user')
    def library_books(self):
        user = request.env.user
        books = request.env['library.book'].search([
            ('reader_id', '=', user.partner_id.id)])
        return request.render('school_lesson_6_4.library_books_page', {
            'company': user.company_id,
            'reader': user.partner_id,
            'books': books,
        })
