# Hệ thống quản lý thư viện trên Odoo 18

Khóa luận: "Nghiên cứu và triển khai hệ thống quản lý thư viện trên nền tảng Odoo ERP".

Module `library_management` quản lý sách, bản sao, độc giả, mượn trả, phiếu phạt và đặt trước, kèm website tra cứu và cổng thông tin cho độc giả.

## Chức năng

**Quản trị (backend)**
- Danh mục: sách (kèm ảnh bìa), tác giả, nhà xuất bản, thể loại, bản sao sách.
- Độc giả: mở rộng từ liên hệ (`res.partner`) với mã độc giả, ngày đăng ký, ghi chú.
- Phiếu mượn: mã `LM` tự sinh; xác nhận mượn, gia hạn 7 ngày (tối đa 2 lần), trả sách, đánh dấu quá hạn; tác vụ định kỳ tự đánh dấu quá hạn mỗi ngày.
- Phiếu phạt: mã `FP` tự sinh; tự tạo khi trả trễ (số ngày trễ x 5.000 đồng); theo dõi thanh toán.
- Đặt trước: mã `DT` tự sinh; chặn đặt trùng cho cùng độc giả và cùng sách.
- Phân quyền: nhóm **Thư viện / Thủ thư** (đọc, ghi) và **Thư viện / Người xem** (chỉ đọc).

**Website**
- `/library`: danh mục và tìm kiếm theo tên hoặc ISBN.
- `/library/book/<id>`: chi tiết sách, số bản có sẵn, đặt trước khi hết bản.
- `/my/loans`: độc giả đăng nhập Portal xem phiếu mượn của chính mình.
- `/library/dashboard`: số liệu tổng quan.

## Yêu cầu

- Odoo 18.0, Python 3.11, PostgreSQL 17.
- Module phụ thuộc: `base`, `website`.

## Cài đặt

1. Chép thư mục này vào `custom_addons` và thêm đường dẫn đó vào `addons_path` trong `odoo.conf`.
2. Khởi động Odoo:

```powershell
python odoo-bin -c odoo.conf -d library_db
```

3. Vào Ứng dụng, bỏ bộ lọc mặc định, tìm **Library Management** và bấm Cài đặt. Hoặc cài bằng dòng lệnh khi Odoo đã dừng:

```powershell
python odoo-bin -c odoo.conf -d library_db -i library_management --stop-after-init
```

4. Khi cập nhật code, nâng cấp module:

```powershell
python odoo-bin -c odoo.conf -d library_db -u library_management --stop-after-init
```

5. Thêm tài khoản quản trị vào nhóm **Thư viện / Thủ thư** để thấy đủ menu.

## Cấp tài khoản cho độc giả

Mở hồ sơ độc giả (cần có email), chọn **Cấp quyền truy cập cổng thông tin**, sau đó đặt mật khẩu cho người dùng vừa tạo. Máy chủ chưa cấu hình gửi email nên không dùng nút gửi thư mời.

## Cấu trúc

```text
library_management/
├── controllers/   # route website
├── data/          # mã tự động, tác vụ định kỳ
├── models/        # sách, bản sao, độc giả, phiếu mượn, phiếu phạt, đặt trước
├── security/      # nhóm người dùng và phân quyền
└── views/         # giao diện quản trị và website (QWeb)
```

## Hạn chế đã biết

- Trạng thái bản sao và ngày trả của phiếu mượn có thể sửa tay trên giao diện.
- Phiếu phạt tự tạo chỉ cho trường hợp trả trễ.
- Đặt trước chưa tự chuyển sang trạng thái Sẵn sàng khi sách được trả; chưa giới hạn số sách mượn tối đa.
- Chưa cấu hình gửi email; trang dashboard đang công khai.
- Quy tắc gia hạn tối đa 2 lần và mức phạt 5.000 đồng/ngày đang chờ giảng viên xác nhận.