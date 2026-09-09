# ERP Odoo Customize

Kho tuỳ biến trên nền **Odoo 19.0 Community**, chạy qua Docker image chính thức
(`odoo:19.0`) — **không vendor source Odoo**, chỉ giữ phần module tuỳ biến ở
`addons/`. Muốn nâng cấp core thì chỉ cần đổi tag image.

## Chạy thử

```bash
cp .env.example .env      # đổi mật khẩu trước khi dùng thật
make up                   # dựng Postgres + Odoo
make logs                 # theo dõi log lúc khởi tạo lần đầu
```

Mở `http://localhost:8069` → tạo database mới → cài module **ERP Customize —
Base** (`erp_customize_base`) từ Apps để kiểm tra mọi thứ chạy đúng.

## Cấu trúc

```
addons/
  erp_customize_base/    ← module khởi điểm (model + view + menu mẫu)
config/
  odoo.conf               ← cấu hình Odoo, mount vào /etc/odoo/odoo.conf
docker-compose.yml
```

## Cách phát triển trên nền Community

Image `odoo:19.0` đã có sẵn TOÀN BỘ mã nguồn Community bên trong container
(`res.partner`, `sale.order`, `product.template`, `account.move`...).
**Không bao giờ sửa trực tiếp core** — luôn viết addon module trong
`addons/` rồi Odoo nạp chồng lên lúc chạy. Hai cách:

1. **Kế thừa model/view có sẵn** — dùng khi Community đã có sẵn khái niệm,
   chỉ cần thêm trường/logic. Ví dụ đã có trong `erp_customize_base`:
   `models/res_partner.py` (`_inherit = 'res.partner'`) +
   `views/res_partner_views.xml` (kế thừa `base.view_partner_form` bằng
   `xpath`, chèn thêm một trường mà không đụng file gốc).
2. **Tạo model mới hoàn toàn** — dùng khi nghiệp vụ chưa tồn tại trong
   Community. Ví dụ: `models/demo_item.py`.

**Đọc mã nguồn gốc để biết field/view nào mà kế thừa** — không cần clone
vào repo này:
- Duyệt trực tiếp trên [github.com/odoo/odoo, nhánh `19.0`](https://github.com/odoo/odoo/tree/19.0/addons)
- Hoặc đọc ngay trong container đang chạy:
  ```bash
  docker compose exec odoo find /usr/lib/python3/dist-packages/odoo/addons/base -name "*.py"
  docker compose exec odoo cat /usr/lib/python3/dist-packages/odoo/addons/base/models/res_partner.py
  ```
- `make shell` mở Odoo shell (Python + ORM sống) để tự kiểm tra field/method
  của bất kỳ model nào: `env['res.partner']._fields.keys()`

## Lệnh hay dùng

| Lệnh | Việc |
|---|---|
| `make up` / `make down` | bật / tắt |
| `make logs` | xem log Odoo |
| `make shell` | mở Odoo shell (Python, có ORM) |
| `make psql` | vào psql của DB |
| `make update MODULE=<tên> DB=<db>` | nâng cấp một module sau khi sửa code |

## Luồng nhánh (Git flow)

Bốn nhánh dài hạn, promote một chiều — chưa có production thật nhưng dựng
sẵn để không phải đổi thói quen khi có:

```
feature/* ──► main ──► develop ──► staging ──► production
```

| Nhánh | Vai trò |
|---|---|
| `main` | Nhánh phát triển chính — mọi PR từ `feature/*` gộp vào đây |
| `develop` | Bản build luôn mới nhất, môi trường dev dùng chung |
| `staging` | Diễn tập trước khi lên thật — chỉ nhận merge từ `develop` |
| `production` | Đang chạy thật — chỉ nhận merge từ `staging`, không commit thẳng |

Quy tắc: **không commit thẳng vào `develop`/`staging`/`production`** —
luôn merge/PR từ nhánh trước nó trong chuỗi. Branch protection cho ba nhánh
này cần bật thủ công trên GitHub (Settings → Branches) vì máy hiện tại
không có `gh` CLI đã đăng nhập.

## Thêm module mới

Tạo thư mục mới trong `addons/`, theo đúng bố cục Odoo chuẩn
(`__manifest__.py`, `models/`, `views/`, `security/ir.model.access.csv`), rồi
`make update MODULE=<tên_module> DB=<db>`.
