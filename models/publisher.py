from odoo import models, fields


class LibraryPublisher(models.Model):
    _name = 'library.publisher'
    _description = 'Nhà xuất bản'

    name = fields.Char(
        string='Tên nhà xuất bản',
        required=True
    )

    description = fields.Text(
        string='Mô tả'
    )