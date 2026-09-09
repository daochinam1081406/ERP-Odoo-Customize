# ERP Odoo Customize

Kho tuỳ biến trên nền **Odoo 19.0 Community**, chạy qua Docker image chính thức
(`odoo:19.0`) — **không vendor source Odoo**, chỉ giữ phần module tuỳ biến ở
`addons/`. Muốn nâng cấp core thì chỉ cần đổi tag image.

**Trọng tâm hệ thống: CRM**, khép vòng sang Sales và Invoicing (không dừng ở
phễu bán hàng — Won phải đi tới được hoá đơn). Xem [Ngăn xếp module](#ngăn-xếp-module).

## Chạy thử

```bash
cp .env.example .env      # đổi mật khẩu trước khi dùng thật
make up                   # dựng Postgres + Odoo
make logs                 # theo dõi log lúc khởi tạo lần đầu
```

Mở `http://localhost:8069` → tạo database mới → cài module **ERP Customize —
CRM** (`erp_customize_crm`) từ Apps — nó tự kéo theo `crm`, `sale_crm`
(→ `sale`, `account`) và `erp_customize_base`.

## Ngăn xếp module

```
erp_customize_crm  ──depends──►  crm
                    ──depends──►  sale_crm  ──depends──►  sale ──► account
                    ──depends──►  erp_customize_base  ──depends──►  base
```

| Module | Của ai | Vai trò |
|---|---|---|
| `crm`, `sale`, `account`, `sale_crm` | Odoo Community (có sẵn trong image) | Phễu bán hàng, báo giá/đơn hàng, hoá đơn — và cầu nối Opportunity → Quotation |
| `erp_customize_base` | Tự viết | Mở rộng danh bạ (`res.partner`) — nền dùng chung cho mọi phân hệ khác |
| `erp_customize_crm` | Tự viết | Cấu hình + tuỳ biến `crm.lead` (chi tiết ngay dưới) |

Vòng khép kín có sẵn **không cần viết gì thêm**: Lead → Opportunity → Won →
nút "Chuyển thành báo giá" (từ `sale_crm`) → Quotation → Confirm → Create
Invoice.

## Quyết định: dựa vào CRM tiên tiến nào, tận dụng gì, thêm gì

So với Salesforce/HubSpot/Pipedrive trước khi viết thêm bất kỳ dòng nào, để
khỏi làm lại thứ Odoo Community đã có (và thường làm tệ hơn bản gốc):

| Tính năng "CRM tiên tiến" | Trong Odoo Community | Việc đã làm |
|---|---|---|
| Cảnh báo deal đọng lâu một giai đoạn (rotting — nổi tiếng ở Pipedrive) | **Có sẵn** (`crm.stage.rotting_threshold_days`, hiện ngay trên statusbar) nhưng **mặc định TẮT** (0 ở mọi giai đoạn) | Bật với ngưỡng 7/14/21 ngày theo 3 giai đoạn đầu — không viết field riêng |
| Chấm điểm lead tự động (lead scoring — Salesforce/HubSpot tính phí riêng) | **Có sẵn miễn phí**, học bằng Naive Bayes từ lịch sử thắng/thua | Không cần làm gì, chỉ cần đủ dữ liệu lịch sử để nó học |
| Phát hiện lead trùng lặp | **Có sẵn** (theo email/SĐT/công ty, smart button trên form) | Không cần làm gì |
| Phễu Lead → Opportunity 2 bước (Salesforce Lead object, HubSpot lifecycle stage) | Có sẵn nhưng **mặc định TẮT** — Odoo đi thẳng vào Opportunity | Bật (`group_use_lead`) — khớp cách CRM tiên tiến tách lead thô khỏi cơ hội đã xác nhận |
| Người giới thiệu cụ thể (referral) | **KHÔNG có** — kể cả CRM tiên tiến, UTM chỉ ghi được *kênh* marketing, không ghi được *người* | Thêm field `referred_by_partner_id` trên `crm.lead` |

Hai mục đầu (rotting threshold, bật phễu Lead) nằm trong `__init__.py` qua
`post_init_hook` — chạy bằng ORM chứ không phải XML `<record>`, vì bản ghi
gốc của module `crm` có thể mang `noupdate="1"` khiến ghi đè qua XML data bị
bỏ qua trong im lặng lúc cài.

**Cố ý CHƯA bật:** Recurring Revenue (MRR) và Rule-based Assignment — cả hai
đều có sẵn nhưng là quyết định **đặc thù mô hình kinh doanh** (có bán theo
gói định kỳ không? cơ cấu đội sale thế nào?), không phải điều "CRM tiên
tiến nào cũng nên bật mặc định". Bật ở Settings khi có câu trả lời thật.

## Cấu trúc

```
addons/
  erp_customize_base/    ← nền dùng chung (mở rộng res.partner)
  erp_customize_crm/     ← trọng tâm: tuỳ biến crm.lead
config/
  odoo.conf               ← cấu hình Odoo, mount vào /etc/odoo/odoo.conf
docker-compose.yml
```

## Cách phát triển trên nền Community

Image `odoo:19.0` đã có sẵn TOÀN BỘ mã nguồn Community bên trong container
(`res.partner`, `sale.order`, `product.template`, `account.move`...).
**Không bao giờ sửa trực tiếp core** — luôn viết addon module trong
`addons/` rồi Odoo nạp chồng lên lúc chạy. Hai cách:

**Kế thừa model/view có sẵn** là cách chuẩn — gần như mọi tuỳ biến CRM/Sales
đều rơi vào nhóm này vì Community đã có sẵn khái niệm, chỉ cần thêm
trường/logic. Hai ví dụ đang có trong repo:
- `erp_customize_base/models/res_partner.py` (`_inherit = 'res.partner'`) +
  view kế thừa `base.view_partner_form` bằng `xpath`
- `erp_customize_crm/models/crm_lead.py` (`_inherit = 'crm.lead'`, thêm
  `referred_by_partner_id`) + view kế thừa `crm.crm_lead_view_form`

Chỉ tạo **model mới hoàn toàn** khi nghiệp vụ chưa tồn tại trong Community
(ví dụ một quy trình duyệt nội bộ đặc thù không map được vào Lead/Order nào).

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
