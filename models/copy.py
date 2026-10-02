from unicodedata import category, normalize

from odoo import api, fields, models


class LibraryBookCopy(models.Model):
    _name = 'library.book.copy'
    _description = 'Bản sao sách'
    _rec_name = 'barcode'

    # ======================================================
    # THÔNG TIN SÁCH
    # ======================================================

    book_id = fields.Many2one(
        'library.book',
        string='Sách',
        required=True,
        ondelete='cascade'
    )

    # ======================================================
    # MÃ BẢN SAO
    # ======================================================

    barcode = fields.Char(
        string='Mã bản sao',
        required=True
    )

    # ======================================================
    # TRẠNG THÁI
    # ======================================================

    state = fields.Selection(
        [
            ('available', 'Có sẵn'),
            ('borrowed', 'Đang mượn'),
            ('lost', 'Mất'),
        ],
        string='Trạng thái',
        default='available',
        required=True
    )

    # ======================================================
    # CHUYỂN CHỮ VỀ DẠNG KHÔNG DẤU
    # Ví dụ:
    # "Có sẵn"      -> "co san"
    # "Đang mượn"   -> "dang muon"
    # "Mất"         -> "mat"
    # ======================================================

    @staticmethod
    def _normalize_search_text(value):
        value = (value or '').strip().lower()

        return ''.join(
            char
            for char in normalize('NFD', value)
            if category(char) != 'Mn'
        )

    # ======================================================
    # TÌM KIẾM BẰNG Ô TÌM KIẾM CHÍNH
    #
    # Có thể tìm:
    # - Tên sách
    # - Mã bản sao
    # - Có sẵn
    # - Đang mượn
    # - Mất
    # ======================================================

    @api.model
    def _search_display_name(self, operator, value):
        # Các trường hợp tìm kiếm thông thường
        if not value:
            return super()._search_display_name(operator, value)

        # Ô tìm kiếm chính của Odoo thường truyền chuỗi
        if not isinstance(value, str):
            return super()._search_display_name(operator, value)

        search_value = value.strip()

        if not search_value:
            return super()._search_display_name(operator, value)

        # Tìm theo:
        # 1. Mã bản sao
        # 2. Tên sách
        domain = [
            '|',
            ('barcode', operator, search_value),
            ('book_id.name', operator, search_value),
        ]

        # Chuẩn hóa chuỗi để nhận cả:
        # "có sẵn" / "co san"
        # "đang mượn" / "dang muon"
        # "mất" / "mat"
        normalized_value = self._normalize_search_text(search_value)

        state_map = {
            'co san': 'available',
            'available': 'available',

            'dang muon': 'borrowed',
            'borrowed': 'borrowed',

            'mat': 'lost',
            'lost': 'lost',
        }

        state_value = state_map.get(normalized_value)

        if state_value:
            domain = [
                '|',
                '|',
                ('barcode', operator, search_value),
                ('book_id.name', operator, search_value),
                ('state', '=', state_value),
            ]

        return domain

    # ======================================================
    # RÀNG BUỘC MÃ BẢN SAO KHÔNG TRÙNG
    # ======================================================

    _sql_constraints = [
        (
            'unique_barcode',
            'unique(barcode)',
            'Mã bản sao không được trùng.'
        ),
    ]