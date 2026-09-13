# ERP Odoo Customize — Bàn giao & quy tắc bắt buộc

> Đọc file này TRƯỚC khi làm bất kỳ task nào trong repo này. Repo này nằm lồng bên trong
> `allinone` nhưng là **kho git riêng, remote riêng** (xem mục 0). Nó có `CLAUDE.md` của chính
> nó vì đó là quy tắc bắt buộc phải giữ ở mọi dự án — phiên sau (hoặc phiên quá tải context phải
> mở lại) đọc đúng một file này là đủ để tiếp tục, không cần dò lại lịch sử chat.

---

## 0. Repo này là gì

- **Remote:** `github.com/daochinam1081406/ERP-Odoo-Customize.git`
- **Vị trí cục bộ:** `/Users/daochinam/allinone/ERP-Odoo-Customize/` — bị chặn khỏi git của
  `allinone` qua dòng `ERP-Odoo-Customize/` trong `.gitignore` gốc (cùng mẫu với
  `D-Pro-Microservice/`). **Không xoá dòng đó** — thiếu nó thì `git add -A` ở mono biến thư mục
  này thành một tham chiếu submodule hỏng.
- **Nền tảng:** Odoo **19.0 Community**, chạy qua Docker image chính thức (`odoo:19.0`).
  **Không vendor source Odoo** — chỉ giữ phần tuỳ biến ở `addons/`.
- **Trọng tâm hệ thống:** CRM, khép vòng sang Sales + Invoicing (không dừng ở phễu bán hàng).

## 1. Luồng nhánh (đã dựng, đang dùng)

```
feature/* ──► main ──► develop ──► staging ──► production
```

4 nhánh đã tồn tại trên remote. **Quy tắc: không commit thẳng vào `develop`/`staging`/
`production`** — luôn merge/fast-forward từ nhánh trước nó. Tính tới lần cập nhật file này:
`main` = `develop` (đã đồng bộ mọi commit), `staging`/`production` **cố ý đứng ở commit cũ**
(`28fed77`) chờ promote có chủ đích — đừng tự ý ff chúng lên mà không có lý do rõ.

Branch protection **chưa bật** (cần GitHub web UI, máy này không có `gh` CLI đăng nhập —
`command -v gh` → not found). Đặt nhánh mặc định cũng chưa làm.

## 2. QUY TẮC BẮT BUỘC khi custom Odoo — đọc kỹ, đây là phần hay bị phá vỡ nhất

### A. Kỹ thuật — vi phạm là lỗi/sập ngay, không phải "nên tránh"

| Quy tắc | Vi phạm thì sao |
|---|---|
| Tên thư mục module = tên gói Python hợp lệ (chữ thường, `_`, không dấu/khoảng trắng, không bắt đầu bằng số) | Odoo `import` nó như module Python — sai tên là lỗi import lúc quét `addons_path` |
| Bắt buộc `__manifest__.py` (đúng tên) ở gốc module + `__init__.py` ở mọi thư mục Python con | Thiếu → Odoo không nhận diện được module |
| `depends` trong manifest phải liệt kê **đủ** mọi module có model/view mình động tới | Thiếu → lỗi lúc cài, hoặc tệ hơn: chạy được lúc dev (module kia tình cờ cài trước) nhưng vỡ khi cài trên máy sạch |
| Không khai `_name` trùng model đã có mà thiếu `_inherit` | Odoo coi là định nghĩa mơ hồ, ném lỗi lúc load |
| Model **mới hoàn toàn** bắt buộc có dòng trong `security/ir.model.access.csv` | Thiếu → mở lên bị từ chối quyền, kể cả Admin |
| External ID (`<record id="...">`) phải duy nhất trong phạm vi nạp | Trùng → lỗi khi nạp XML |

**Lưu ý riêng cho model chỉ `_inherit` (không tạo model mới):** KHÔNG cần thêm dòng
`ir.model.access.csv` — quyền đã có sẵn từ module gốc định nghĩa model đó. Đây là lý do
`erp_customize_base` và `erp_customize_crm` hiện **không có** thư mục `security/`.

### B. Không phải rule cứng của engine, nhưng bắt buộc nếu muốn sống qua các lần nâng cấp

- **TUYỆT ĐỐI không sửa trực tiếp file core** trong container. Kỹ thuật thì Community cho sửa
  (mã mở), nhưng đổi tag image (`odoo:19.0` → `odoo:20.0`) là mọi sửa đổi trực tiếp **biến mất
  không dấu vết**. Toàn bộ repo này chỉ có `addons/` — đúng lý do.
- **Luôn gọi `super()`** khi override method (`create`/`write`/`unlink`/bất kỳ). Module khác có
  thể cũng `_inherit` cùng model — bỏ `super()` là cắt đứt chuỗi kế thừa phía sau.
- **Luôn `_inherit`, không copy-paste model gốc rồi sửa** — copy thì mất liên kết với bản gốc,
  Odoo vá lỗi bảo mật ở core thì bản copy không được vá theo.
- **Tra source thật trước khi viết XML kế thừa view** (`xpath`/external ID). Đoán tên field/view
  rồi cài lỗi ngay lúc chạy — không phải lỗi "có thể", là lỗi **chắc chắn xảy ra** nếu đoán sai.
  Cách tra không cần chạy container: `https://raw.githubusercontent.com/odoo/odoo/19.0/addons/<module>/...`
  qua WebFetch. Hai field/view đã xác minh và đang dùng: `res.partner` ↔ `base.view_partner_form`,
  `crm.lead` ↔ `crm.crm_lead_view_form` (group `opportunity_partner` quanh `partner_id`).

### C. Pháp lý — điểm hay bị hiểu nhầm

Community = **LGPL-3**. LGPL **KHÔNG bắt buộc** module tuỳ biến cũng phải mở nguồn — khác GPL,
LGPL cho phép "linking" (tức `_inherit`/`depends`) từ mã đóng nguồn. `license: 'LGPL-3'` trong
hai manifest hiện tại là **lựa chọn**, không phải bắt buộc — đổi sang `'OPL-1'` (giấy phép riêng
của Odoo cho module thương mại) hoặc `'Other proprietary'` bất kỳ lúc nào nếu không muốn công
khai mã. Chỉ khi dùng **Enterprise** (không phải Community) mới bị ràng buộc EULA thật sự — repo
này chưa đụng Enterprise.

### D. Chuẩn coding chính thức của Odoo

Không bắt buộc để chạy — chỉ bắt buộc nếu sau này muốn đóng góp lên Odoo Apps Store/OCA
(`pylint-odoo`, thứ tự khai field/method trong class...). Chưa cần áp dụng ở quy mô hiện tại.

## 3. Nguyên tắc thiết kế đã chốt (đừng "sửa lại" nếu không có lý do mới)

- **Trước khi viết field/logic mới: kiểm Odoo Community đã có sẵn chưa.** Đã xảy ra thật một
  lần (xem mục 5) — viết `days_in_stage` rồi phải rút lại vì trùng với `rotting_threshold_days`
  có sẵn (chỉ đang tắt). Tra source thật (mục 2.B) trước khi quyết định viết mới.
- **Bật tính năng có sẵn nhưng mặc định tắt → dùng `post_init_hook` (Python/ORM), KHÔNG dùng
  XML `<record>` ghi đè.** Bản ghi gốc của module khác (vd. `crm.stage`) có thể mang
  `noupdate="1"`, khiến ghi đè qua XML data bị bỏ qua **trong im lặng** lúc cài — lỗi không hiện
  ra ở đâu cả, chỉ phát hiện khi kiểm tra thủ công giá trị sau khi cài.
- **Mỗi bounded concern một module riêng** — không nhét tuỳ biến CRM vào `erp_customize_base`.
  `erp_customize_base` chỉ giữ thứ dùng chung mọi phân hệ (hiện: mở rộng `res.partner`).
- **Module mới → module đó tự khai `depends` cho đúng những gì nó THẬT SỰ dùng**, dù module
  khác trong repo đã kéo theo sẵn qua chuỗi phụ thuộc. Rõ ràng hơn tiết kiệm dòng.

## 4. Ngăn xếp module hiện tại

```
erp_customize_crm  ──depends──►  crm
                    ──depends──►  sale_crm  ──depends──►  sale ──► account
                    ──depends──►  erp_customize_base  ──depends──►  base
```

| Module | Của ai | Nội dung |
|---|---|---|
| `crm`, `sale`, `account`, `sale_crm` | Odoo Community (có sẵn trong image) | Phễu bán hàng, báo giá/đơn hàng, hoá đơn, cầu nối Opportunity → Quotation |
| `erp_customize_base` | Tự viết | `res.partner` +1 field `internal_reference` (Mã nội bộ) |
| `erp_customize_crm` | Tự viết | Xem mục 5 |

**Cài `erp_customize_crm` là đủ** — nó kéo theo toàn bộ chuỗi phụ thuộc, không cần cài tay
từng app.

## 5. Quyết định đã chốt cho CRM (so với Salesforce/HubSpot/Pipedrive trước khi viết)

| Tính năng "CRM tiên tiến" | Trong Odoo Community | Đã làm |
|---|---|---|
| Cảnh báo deal đọng lâu (rotting — nổi tiếng ở Pipedrive) | Có sẵn (`crm.stage.rotting_threshold_days`) nhưng mặc định TẮT (0 mọi giai đoạn) | Bật theo dữ liệu B2B thật, khác nhau từng giai đoạn — xem mục 6 |
| Chấm điểm lead tự động (lead scoring) | Có sẵn miễn phí, Naive Bayes học từ lịch sử thắng/thua | Không cần làm gì — cần đủ dữ liệu lịch sử để nó học |
| Phát hiện lead trùng lặp | Có sẵn (email/SĐT/công ty, smart button) | Không cần làm gì |
| Phễu Lead → Opportunity 2 bước | Có sẵn nhưng mặc định TẮT | Bật (`group_use_lead`) qua `post_init_hook` |
| Người giới thiệu cụ thể (referral) | KHÔNG có — UTM chỉ ghi kênh marketing, không ghi người | Field mới `referred_by_partner_id` trên `crm.lead` |
| Pipeline 4 giai đoạn quá thô | Chuẩn thực hành B2B là 5-7 giai đoạn | Thiết kế lại 6 giai đoạn + tự động hoá "phản hồi tức thì" — xem mục 6 |

**Cố ý CHƯA bật:** Recurring Revenue (`group_use_recurring_revenues`), Rule-based Assignment
(`crm_use_auto_assignment`) — cả hai là quyết định đặc thù mô hình kinh doanh (bán gói định kỳ?
cơ cấu đội sale ra sao?), chưa có câu trả lời thật từ chủ dự án nên không tự áp đặt.

**Field/view đã xác minh trên source Odoo 19 thật** (không đoán — xem mục 2.B):
`crm.lead.date_last_stage_update`, `crm.stage.rotting_threshold_days`,
`res_config_settings.group_use_lead`, view `crm.crm_lead_view_form` + group `opportunity_partner`,
`mail.activity.mixin.activity_schedule()`, xmlid `mail.mail_activity_data_call`.

## 6. Pipeline 6 giai đoạn — thiết kế theo dữ liệu B2B thật (10/09/2026)

Chốt sau khi được chủ dự án yêu cầu "tự phân tích dữ liệu thật và thiết kế một business tốt" —
tra thực hành B2B 2026 (5-7 giai đoạn là chuẩn) và khảo sát HBR trên 2.241 công ty Mỹ về tốc độ
phản hồi lead trước khi định số, không đoán theo cảm tính.

**Phát hiện đổi hẳn thiết kế:** liên hệ trong GIỜ ĐẦU tăng 7 lần khả năng nói chuyện được người
quyết định; chờ quá 24 GIỜ thì khả năng đủ điều kiện giảm 60 LẦN; 78% khách B2B mua của bên phản
hồi ĐẦU TIÊN. → "Lead mới" phải có ngưỡng đọng chặt nhất (1 ngày, không phải 7 ngày như bản nháp
đầu — đó là số đoán, không phải số có căn cứ) và phải có tự động hoá, không chỉ cảnh báo tĩnh.

| # | Giai đoạn | rotting_threshold_days | Nguồn |
|---|---|---|---|
| 1 | Lead mới | **1** | crm.stage_lead1 (đổi tên) |
| 2 | Đã xác nhận nhu cầu | 10 | crm.stage_lead2 (đổi tên) |
| 3 | Khảo sát yêu cầu | 14 | `data/crm_stage_data.xml` (record mới) |
| 4 | Đã gửi báo giá | 14 | crm.stage_lead3 (đổi tên, sequence 3→4) |
| 5 | Đàm phán | 10 | `data/crm_stage_data.xml` (record mới) |
| 6 | Chốt thắng | 0 (tắt) | crm.stage_lead4 (đổi tên) |

**Tự động hoá:** `crm_lead.py` override `create()` → mọi lead/opportunity mới tự sinh activity
"Gọi ngay" (`mail.mail_activity_data_call`), hạn hôm nay, gán `user_id` (hoặc người tạo nếu
chưa gán). Đây là phần quan trọng nhất của thiết kế này — biến số liệu thành HÀNH VI hệ thống,
không chỉ hiển thị cảnh báo mà trông chờ người dùng tự nhớ kiểm tra.

**4 giai đoạn gốc của Odoo giữ nguyên record (đổi tên qua `post_init_hook`), không xoá** — xoá
record thuộc module khác là hỏng liên kết ngược của mọi dữ liệu cũ trỏ vào nó. 2 giai đoạn mới
là record hoàn toàn mới, module này sở hữu.

✅ **Đã chạy thật (10/09/2026):** xoá `testdb`, cài lại từ đầu (bắt buộc — `post_init_hook` chỉ
chạy lúc cài mới, không chạy lúc `-u`). Kiểm qua `odoo shell`: 6 giai đoạn đúng thứ tự/ngưỡng/tên/
tiêu chí thoát · tạo lead thật → activity "Gọi ngay" tự sinh đúng, hạn hôm nay, tóm tắt đúng nội
dung đã viết trong code.

## 7. Đánh giá "đủ enterprise chưa" (13/09/2026) + bộ kiểm thử tự động

**Chưa đủ.** Đây là MVP kỹ thuật vững (đúng kiến trúc, tận dụng đúng tính năng có sẵn), nhưng mới
phục vụ một người dùng trên một máy. Ba khoảng trống nặng nhất: (1) không có kênh lead thật chảy
vào — chỉ tạo tay/CLI, (2) chưa có ≥2 người dùng thật với phân quyền đã kiểm chứng ở quy mô, (3)
chưa triển khai ra khỏi Docker cục bộ (không HTTPS, không backup, 1 process/không cấu hình
worker). Đã quyết KHÔNG viết `ir.rule` riêng cho phân quyền — cơ chế có sẵn của Odoo
(`sales_team.group_sale_salesman` + rule "Personal Leads") đã đúng, chỉ cần **kiểm và khoá lại
bằng test**, không cần viết thêm.

**Bộ kiểm thử tự động: `addons/erp_customize_crm/tests/test_crm_lead.py`** — 7 test, **7/7 đạt**
(xác nhận 13/09/2026). Khoá lại cả logic mới viết LẪN hành vi có sẵn của Odoo đang dựa vào:

| Test | Khoá lại điều gì |
|---|---|
| `test_referred_by_partner_id_roundtrip` | Field mới ghi/đọc đúng |
| `test_pipeline_has_six_stages_in_order` | 6 giai đoạn, đúng tên, đúng thứ tự |
| `test_first_stage_has_tightest_rotting_threshold` | "Lead mới" = ngưỡng chặt nhất (1 ngày) — con số có căn cứ, không phải đoán |
| `test_won_stage_has_no_rotting_threshold` | Giai đoạn chốt không mang khái niệm "đọng" |
| `test_create_schedules_first_contact_activity` | Cơ chế tự động hoá quan trọng nhất — activity "Gọi ngay" tự sinh |
| `test_bare_internal_user_has_no_crm_access_by_default` | Đóng mặc định — nhân viên chưa gán quyền Sales thì 0 quyền truy cập |
| `test_salesperson_cannot_see_colleague_opportunity` | Cách ly dữ liệu giữa các nhân viên — cơ chế CÓ SẴN của Odoo, khoá lại để không ai vô tình phá |

**⚠️ BẪY CHẠY TEST — `--test-enable` cố mở cổng 8069 DÙ ĐÃ CÓ `--no-http`.** Container chính
(`erp-odoo-customize-odoo-1`) đã chiếm cổng đó; `docker compose exec` vào container đang sống sẽ
đụng độ ngay cả khi khai `--no-http`. Cách đúng: chạy trong container TẠM THỜI riêng, không có
container đang sống nào tranh cổng:
```bash
docker compose run --rm odoo odoo server -c /etc/odoo/odoo.conf -d test_ci \
  -i erp_customize_crm --test-enable --test-tags=/erp_customize_crm \
  --stop-after-init --without-demo=True
# Dọn sau khi chạy xong:
docker compose exec -T db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS test_ci;"
```

**⚠️ BẪY ĐỔI TÊN FIELD Ở ODOO 19 — tài liệu/tutorial cũ sẽ chỉ sai:**
- `res.users.groups_id` → **`group_ids`**
- `res.groups.category_id` → **`privilege_id`**; `res.groups.users` → **`user_ids`**
- CLI không còn phẳng — có subcommand: `odoo server ...`, `odoo shell ...`, `odoo module ...`
  (chạy `odoo -d ... -i ...` không khai subcommand vẫn ngầm hiểu là `server`, nhưng khai tường
  minh an toàn hơn khi kết hợp nhiều cờ)

**✅ Đã xác nhận:** `l10n_vn` (bản địa hoá kế toán VN) có sẵn trong image, cài sạch khi
`company.country_id` = Việt Nam — không cần làm gì thêm, chỉ cần set quốc gia công ty đúng lúc
onboarding rồi cài module.

---

## 🔖 BÀN GIAO — đọc mục này trước khi làm tiếp

**Điểm dừng (phiên 13/09/2026):** Bộ kiểm thử tự động (7 test) đã viết và **chạy PASS thật**
(7/7, xem mục 7) — nhưng thời điểm ghi dòng này CHƯA commit/push (xem lệnh ở cuối mục). Nếu
`git log` đã có commit nhắc tới "test_crm_lead" thì đã xong bước đó, xoá cảnh báo này.

**✅ Đã chạy thật (13/09/2026):**
- Xác nhận cơ chế phân quyền CÓ SẴN của Odoo đủ tốt cho nhiều người dùng — không cần viết
  `ir.rule` riêng (mục 7)
- Viết + chạy PASS 7/7 test tự động, khoá lại toàn bộ hành vi cốt lõi (pipeline, tự động hoá,
  phân quyền)
- Xác nhận `l10n_vn` cài sạch khi company country = Việt Nam

**Lần chạy trước (10/09/2026):** pipeline 6 giai đoạn + activity "Gọi ngay" — xem mục 6.

**Việc tiếp theo:**
1. `git add -A && git commit` cho bộ test + các phát hiện mục 7 nếu chưa commit (kiểm
   `git status` trước — việc ĐẦU TIÊN nếu đang đọc file này ở phiên mới).
2. Quyết `stock` (Inventory) — có hàng hoá vật lý cần giao hay dịch vụ thuần? Nếu có hàng hoá:
   thêm `stock` vào `depends` của `erp_customize_crm` hoặc module riêng.
3. Pipeline 6 giai đoạn hiện là **thiết kế tổng quát dựa trên thực hành B2B chung** — chưa phải
   quy trình đặc thù của chủ dự án. Khi có mô tả quy trình thật, so sánh và điều chỉnh tên/số
   giai đoạn, KHÔNG giữ nguyên chỉ vì "đã chạy được".
4. Ba khoảng trống enterprise nặng nhất còn lại (mục 7): kênh lead thật chảy vào (web form/email),
   triển khai ra khỏi Docker cục bộ an toàn (HTTPS/backup/workers), tích hợp Zalo/WhatsApp/SMTP
   thật — cả ba đều cần tài khoản/hạ tầng bên ngoài chưa có ở đây.
5. Trả lời được việc kinh doanh thật thì mới bật Recurring Revenue / Rule-based Assignment
   (xem mục 5).
6. Bật branch protection cho `develop`/`staging`/`production` trên GitHub web UI (mục 1).

**File cá nhân/bí mật:** `.env` (đã gitignore, chưa tạo — chỉ có `.env.example`). Không có gì
khác cần né trong repo này tính tới giờ.
