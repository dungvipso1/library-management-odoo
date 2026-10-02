from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Phiếu mượn sách'
    _rec_name = 'name'

    name = fields.Char(
        string='Mã phiếu mượn',
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

    copy_id = fields.Many2one(
        'library.book.copy',
        string='Bản sao sách',
        required=True,
    )

    book_id = fields.Many2one(
        'library.book',
        string='Sách',
        related='copy_id.book_id',
        store=True,
        readonly=True,
    )

    checkout_date = fields.Date(
        string='Ngày mượn',
        default=fields.Date.today,
        required=True,
    )

    due_date = fields.Date(
        string='Hạn trả',
        default=lambda self: (
            fields.Date.to_date(fields.Date.today())
            + timedelta(days=14)
        ),
        required=True,
    )

    return_date = fields.Date(
        string='Ngày trả',
    )

    state = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('borrowed', 'Đang mượn'),
            ('returned', 'Đã trả'),
            ('overdue', 'Quá hạn'),
        ],
        string='Trạng thái',
        default='draft',
        required=True,
    )

    renewal_count = fields.Integer(
        string='Số lần gia hạn',
        default=0,
        readonly=True,
    )

    fine_ids = fields.One2many(
        'library.fine',
        'loan_id',
        string='Phiếu phạt',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'library.loan'
                    )
                    or 'New'
                )

        return super().create(vals_list)

    @api.constrains('checkout_date', 'due_date')
    def _check_dates(self):
        for record in self:
            checkout_date = (
                fields.Date.to_date(record.checkout_date)
                if record.checkout_date
                else False
            )

            due_date = (
                fields.Date.to_date(record.due_date)
                if record.due_date
                else False
            )

            if checkout_date and due_date and due_date < checkout_date:
                raise ValidationError(
                    'Hạn trả không được trước ngày mượn.'
                )

    def action_checkout(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(
                    'Chỉ có thể xác nhận phiếu đang ở trạng thái Nháp.'
                )

            if record.copy_id.state != 'available':
                raise ValidationError(
                    'Bản sao sách này hiện không có sẵn để mượn.'
                )

            if not record.member_id.is_library_member:
                raise ValidationError(
                    'Đối tượng được chọn chưa được đăng ký là độc giả.'
                )

            record.copy_id.state = 'borrowed'
            record.state = 'borrowed'

    def action_extend(self):
        """Gia hạn phiếu mượn thêm 7 ngày."""
        for record in self:
            if record.state != 'borrowed':
                raise ValidationError(
                    'Chỉ có thể gia hạn phiếu đang ở trạng thái Đang mượn.'
                )

            if record.renewal_count >= 2:
                raise ValidationError(
                    'Phiếu mượn này đã được gia hạn tối đa 2 lần.'
                )

            today = fields.Date.to_date(fields.Date.today())
            due_date = fields.Date.to_date(record.due_date)

            if due_date < today:
                raise ValidationError(
                    'Phiếu đã quá hạn nên không thể gia hạn.'
                )

            record.due_date = due_date + timedelta(days=7)
            record.renewal_count += 1

    def action_return(self):
        for record in self:
            if record.state not in ('borrowed', 'overdue'):
                raise ValidationError(
                    'Phiếu này không ở trạng thái đang mượn hoặc quá hạn.'
                )

            return_date = fields.Date.to_date(fields.Date.today())
            due_date = (
                fields.Date.to_date(record.due_date)
                if record.due_date
                else False
            )

            record.return_date = return_date

            if due_date and return_date > due_date:
                overdue_days = (return_date - due_date).days

                existing_fine = self.env['library.fine'].search(
                    [
                        ('loan_id', '=', record.id),
                        ('reason', '=', 'late'),
                    ],
                    limit=1,
                )

                if not existing_fine:
                    self.env['library.fine'].create(
                        {
                            'loan_id': record.id,
                            'reason': 'late',
                            'overdue_days': overdue_days,
                            'amount': overdue_days * 5000,
                            'state': 'unpaid',
                            'note': (
                                f'Trả sách trễ {overdue_days} ngày.'
                            ),
                        }
                    )

            record.copy_id.state = 'available'
            record.state = 'returned'

    def action_mark_overdue(self):
        for record in self:
            if record.state != 'borrowed':
                continue

            if not record.due_date:
                continue

            due_date = fields.Date.to_date(record.due_date)
            today = fields.Date.to_date(fields.Date.today())

            if due_date < today:
                record.state = 'overdue'

    @api.model
    def _cron_check_overdue(self):
        """Tự động đánh dấu các phiếu đã quá hạn."""
        today = fields.Date.to_date(fields.Date.today())

        overdue_loans = self.search(
            [
                ('state', '=', 'borrowed'),
                ('due_date', '<', today),
            ]
        )

        for loan in overdue_loans:
            loan.state = 'overdue'