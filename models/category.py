from odoo import models, fields


class LibraryCategory(models.Model):
    _name = 'library.category'
    _description = 'Thể loại sách'

    name = fields.Char(
        string='Tên thể loại',
        required=True
    )

    description = fields.Text(
        string='Mô tả'
    )