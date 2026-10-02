from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LibraryReservation(models.Model):
    _name = 'library.reservation'
    _description = 'Đặt trước sách'
    _rec_name = 'name'
    _order = 'reserve_date desc'

    name = fields.Char(
        string='Mã đặt trước',
        required=True,
        default='New',
        copy=False,
    )

    member_id = fields.Many2one(
        'res.partner',
        string='Độc giả',
        required=True,
        domain=[('is_library_member', '=', True)],
    )

    book_id = fields.Many2one(
        'library.book',
        string='Sách',
        required=True,
    )

    reserve_date = fields.Date(
        string='Ngày đặt',
        default=fields.Date.today,
        required=True,
    )

    state = fields.Selection(
        [
            ('pending', 'Chờ xử lý'),
            ('ready', 'Sẵn sàng'),
            ('done', 'Đã hoàn thành'),
            ('cancelled', 'Đã hủy'),
        ],
        string='Trạng thái',
        default='pending',
        required=True,
    )

    note = fields.Text(
        string='Ghi chú',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'library.reservation'
                    )
                    or 'New'
                )

        return super().create(vals_list)

    @api.constrains('member_id', 'book_id', 'state')
    def _check_duplicate_reservation(self):
        for record in self:
            if record.state != 'pending':
                continue

            duplicate = self.search(
                [
                    ('id', '!=', record.id),
                    ('member_id', '=', record.member_id.id),
                    ('book_id', '=', record.book_id.id),
                    ('state', '=', 'pending'),
                ],
                limit=1,
            )

            if duplicate:
                raise ValidationError(
                    'Độc giả này đã có một yêu cầu đặt trước '
                    'đang chờ xử lý cho sách này.'
                )

    def action_mark_ready(self):
        for record in self:
            record.state = 'ready'

    def action_mark_done(self):
        for record in self:
            record.state = 'done'

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'