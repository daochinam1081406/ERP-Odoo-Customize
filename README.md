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
