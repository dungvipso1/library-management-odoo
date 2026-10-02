from odoo import models, fields


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Tác giả'

    name = fields.Char(
        string='Tên tác giả',
        required=True
    )

    description = fields.Text(
        string='Mô tả'
    )