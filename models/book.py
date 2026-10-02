from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Sách thư viện'

    # ======================================================
    # THÔNG TIN CƠ BẢN
    # ======================================================

    name = fields.Char(
        string='Tên sách',
        required=True
    )

    isbn = fields.Char(
        string='ISBN'
    )

    image = fields.Image(
        string='Ảnh bìa'
    )

    publication_year = fields.Integer(
        string='Năm xuất bản'
    )

    description = fields.Text(
        string='Mô tả'
    )

    # ======================================================
    # QUAN HỆ VỚI TÁC GIẢ
    # ======================================================

    author_ids = fields.Many2many(
        'library.author',
        string='Tác giả'
    )

    # ======================================================
    # QUAN HỆ VỚI NHÀ XUẤT BẢN
    # ======================================================

    publisher_id = fields.Many2one(
        'library.publisher',
        string='Nhà xuất bản'
    )

    # ======================================================
    # QUAN HỆ VỚI THỂ LOẠI
    # ======================================================

    category_id = fields.Many2one(
        'library.category',
        string='Thể loại'
    )

    # ======================================================
    # QUAN HỆ VỚI BẢN SAO SÁCH
    # ======================================================

    copy_ids = fields.One2many(
        'library.book.copy',
        'book_id',
        string='Các bản sao'
    )

    # ======================================================
    # SỐ LƯỢNG BẢN SAO
    # Tự động tính từ số lượng bản sao thực tế
    # ======================================================

    quantity = fields.Integer(
        string='Số lượng',
        compute='_compute_quantity',
        store=True
    )

    @api.depends('copy_ids')
    def _compute_quantity(self):
        for record in self:
            record.quantity = len(record.copy_ids)

    # ======================================================
    # RÀNG BUỘC DỮ LIỆU TRONG DATABASE
    # ======================================================

    _sql_constraints = [
        (
            'unique_isbn',
            'unique(isbn)',
            'ISBN không được trùng.'
        ),
        (
            'positive_quantity',
            'CHECK(quantity >= 0)',
            'Số lượng không được âm.'
        ),
    ]

    # ======================================================
    # KIỂM TRA NĂM XUẤT BẢN
    # ======================================================

    @api.constrains('publication_year')
    def _check_publication_year(self):
        current_year = datetime.now().year

        for record in self:
            if record.publication_year and (
                record.publication_year <= 0
                or record.publication_year > current_year
            ):
                raise ValidationError(
                    'Năm xuất bản phải lớn hơn 0 '
                    'và không được vượt quá năm hiện tại.'
                )