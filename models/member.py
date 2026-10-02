from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_library_member = fields.Boolean(
        string='Là độc giả thư viện'
    )

    member_code = fields.Char(
        string='Mã độc giả',
        copy=False
    )

    member_date = fields.Date(
        string='Ngày đăng ký'
    )

    member_note = fields.Text(
        string='Ghi chú độc giả'
    )