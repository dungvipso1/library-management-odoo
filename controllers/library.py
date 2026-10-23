from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError


class LibraryWebsiteController(http.Controller):

    @http.route(
        '/library',
        type='http',
        auth='public',
        website=True,
    )
    def library_catalog(self, q=None, **kwargs):
        domain = []

        if q:
            domain = [
                '|',
                ('name', 'ilike', q),
                ('isbn', 'ilike', q),
            ]

        books = request.env['library.book'].sudo().search(
            domain,
            order='name asc',
        )

        return request.render(
            'library_management.library_catalog',
            {
                'books': books,
                'search_query': q or '',
            },
        )

    @http.route(
        '/library/book/<int:book_id>',
        type='http',
        auth='public',
        website=True,
    )
    def library_book_detail(self, book_id, **kwargs):
        book = request.env['library.book'].sudo().browse(book_id)

        if not book.exists():
            return request.not_found()

        available_copies = book.copy_ids.filtered(
            lambda copy: copy.state == 'available'
        )

        return request.render(
            'library_management.library_book_detail',
            {
                'book': book,
                'available_copies': available_copies,
                'reservation_message': kwargs.get(
                    'reservation_message'
                ),
            },
        )

    @http.route(
        '/library/book/<int:book_id>/reserve',
        type='http',
        auth='user',
        website=True,
        methods=['POST'],
    )
    def library_book_reserve(self, book_id, **kwargs):
        book = request.env['library.book'].sudo().browse(book_id)

        if not book.exists():
            return request.not_found()

        partner = request.env.user.partner_id

        if not partner.is_library_member:
            return request.redirect(
                '/library/book/%s?reservation_message='
                'Tài khoản hiện tại chưa được đăng ký là độc giả.'
                % book.id
            )

        available_copies = book.copy_ids.filtered(
            lambda copy: copy.state == 'available'
        )

        if available_copies:
            return request.redirect(
                '/library/book/%s?reservation_message='
                'Sách hiện đang có bản sao sẵn có, bạn có thể liên hệ '
                'thủ thư để mượn sách.'
                % book.id
            )

        try:
            # SỬA: thêm sudo() vì user Portal không có quyền tạo đặt trước.
            # member_id luôn là partner của người đang đăng nhập.
            request.env['library.reservation'].sudo().create(
                {
                    'member_id': partner.id,
                    'book_id': book.id,
                    'note': 'Đặt trước từ website thư viện.',
                }
            )
        except ValidationError as error:
            return request.redirect(
                '/library/book/%s?reservation_message=%s'
                % (book.id, str(error))
            )

        return request.redirect(
            '/library/book/%s?reservation_message='
            'Đặt trước sách thành công.'
            % book.id
        )

    @http.route(
        '/my/loans',
        type='http',
        auth='user',
        website=True,
    )
    def my_library_loans(self, **kwargs):
        partner = request.env.user.partner_id

        # SỬA: thêm sudo() để Portal đọc được phiếu mượn.
        # Vẫn lọc cứng theo member_id = partner đang đăng nhập,
        # nên mỗi người chỉ thấy phiếu của chính mình.
        loans = request.env['library.loan'].sudo().search(
            [
                ('member_id', '=', partner.id),
            ],
            order='checkout_date desc',
        )

        return request.render(
            'library_management.library_my_loans',
            {
                'partner': partner,
                'loans': loans,
            },
        )

    @http.route(
        '/library/dashboard',
        type='http',
        auth='public',
        website=True,
    )
    def library_dashboard(self, **kwargs):
        Book = request.env['library.book'].sudo()
        Copy = request.env['library.book.copy'].sudo()
        Partner = request.env['res.partner'].sudo()
        Loan = request.env['library.loan'].sudo()

        total_books = Book.search_count([])

        total_copies = Copy.search_count([])

        borrowed_copies = Copy.search_count(
            [('state', '=', 'borrowed')]
        )

        overdue_loans = Loan.search_count(
            [('state', '=', 'overdue')]
        )

        total_members = Partner.search_count(
            [('is_library_member', '=', True)]
        )

        return request.render(
            'library_management.library_dashboard',
            {
                'total_books': total_books,
                'total_copies': total_copies,
                'borrowed_copies': borrowed_copies,
                'overdue_loans': overdue_loans,
                'total_members': total_members,
            },
        )