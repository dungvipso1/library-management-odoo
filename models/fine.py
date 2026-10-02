from odoo import api, fields, models


class LibraryFine(models.Model):
    _name = 'library.fine'
    _description = 'Phiếu phạt thư viện'
    _rec_name = 'name'

    name = fields.Char(
        string='Mã phiếu phạt',
        required=True,
        default='New',
        copy=False,
    )

    loan_id = fields.Many2one(
        'library.loan',
        string='Phiếu mượn',
        required=True,
        ondelete='cascade',
    )

    member_id = fields.Many2one(
        'res.partner',
        string='Độc giả',
        related='loan_id.member_id',
        store=True,
        readonly=True,
    )

    book_id = fields.Many2one(
        'library.book',
        string='Sách',
        related='loan_id.book_id',
        store=True,
        readonly=True,
    )

    reason = fields.Selection(
        [
            ('late', 'Trả sách quá hạn'),
            ('damaged', 'Làm hỏng sách'),
            ('lost', 'Mất sách'),
        ],
        string='Lý do',
        required=True,
        default='late',
    )

    overdue_days = fields.Integer(
        string='Số ngày quá hạn',
        default=0,
    )

    amount = fields.Float(
        string='Số tiền phạt',
        required=True,
        default=0,
    )

    state = fields.Selection(
        [
            ('unpaid', 'Chưa thanh toán'),
            ('paid', 'Đã thanh toán'),
        ],
        string='Trạng thái',
        required=True,
        default='unpaid',
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
                        'library.fine'
                    )
                    or 'New'
                )

        return super().create(vals_list)

    def action_mark_paid(self):
        for record in self:
            record.state = 'paid'

    def action_mark_unpaid(self):
        for record in self:
            record.state = 'unpaid'