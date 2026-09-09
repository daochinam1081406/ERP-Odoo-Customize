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
| Cảnh báo deal đọng lâu (rotting — nổi tiếng ở Pipedrive) | Có sẵn (`crm.stage.rotting_threshold_days`) nhưng mặc định TẮT (0 mọi giai đoạn) | Bật 7/14/21 ngày cho New/Qualified/Proposition qua `post_init_hook` |
| Chấm điểm lead tự động (lead scoring) | Có sẵn miễn phí, Naive Bayes học từ lịch sử thắng/thua | Không cần làm gì — cần đủ dữ liệu lịch sử để nó học |
| Phát hiện lead trùng lặp | Có sẵn (email/SĐT/công ty, smart button) | Không cần làm gì |
| Phễu Lead → Opportunity 2 bước | Có sẵn nhưng mặc định TẮT | Bật (`group_use_lead`) qua `post_init_hook` |
| Người giới thiệu cụ thể (referral) | KHÔNG có — UTM chỉ ghi kênh marketing, không ghi người | Field mới `referred_by_partner_id` trên `crm.lead` |

**Cố ý CHƯA bật:** Recurring Revenue (`group_use_recurring_revenues`), Rule-based Assignment
(`crm_use_auto_assignment`) — cả hai là quyết định đặc thù mô hình kinh doanh (bán gói định kỳ?
cơ cấu đội sale ra sao?), chưa có câu trả lời thật từ chủ dự án nên không tự áp đặt.

**Field/view đã xác minh trên source Odoo 19 thật** (không đoán — xem mục 2.B):
`crm.lead.date_last_stage_update`, `crm.stage.rotting_threshold_days`,
`res_config_settings.group_use_lead`, view `crm.crm_lead_view_form` + group `opportunity_partner`.

---

## 🔖 BÀN GIAO — đọc mục này trước khi làm tiếp

**Điểm dừng (phiên 09/09/2026):** Toàn bộ mã đã push lên `main` + `develop` (đồng bộ, commit
`6399164`). `staging`/`production` cố ý đứng ở commit trước (`28fed77`).

**⚠️ CHƯA CHẠY THỬ TRÊN ODOO THẬT — đây là việc quan trọng nhất còn lại.** Mọi kiểm chứng tới
giờ chỉ là tĩnh: `python3 -m py_compile` cho từng file `.py`, và `xml.etree.ElementTree.parse`
cho từng file `.xml` — cả hai chỉ bắt lỗi cú pháp, **không** bắt được: external ID tham chiếu sai
(`inherit_id`, `xpath`), field không tồn tại trên model, lỗi `depends` thiếu, `post_init_hook`
chạy sai (vd. `env.ref()` không tìm thấy do sai id). Đúng nguyên tắc dự án chị/anh vẫn áp dụng ở
D-Pro: **"chạy thật mới biết, build xanh không có nghĩa gì"**.

**Việc đầu tiên của phiên tiếp theo (hoặc phiên này nếu còn context):**
```bash
cd /Users/daochinam/allinone/ERP-Odoo-Customize
cp .env.example .env
make up && make logs
```
Rồi vào `http://localhost:8069` → tạo DB → cài `erp_customize_crm` → kiểm:
1. Cài không lỗi (đặc biệt `post_init_hook` chạy xong không exception)
2. Vào Settings → CRM: đã bật "Leads" (`group_use_lead`) chưa
3. Mở một giai đoạn Pipeline (Cấu hình → Giai đoạn): New/Qualified/Proposition có
   `rotting_threshold_days` = 7/14/21 chưa
4. Mở form một Opportunity: có field "Được giới thiệu bởi" ngay sau "Liên hệ" chưa
5. Contacts: mở một liên hệ, có field "Mã nội bộ" chưa

Nếu cả 5 đều đúng → cập nhật dòng "⚠️ CHƯA CHẠY THỬ" ở trên thành "✅ Đã chạy thật (ngày...)"
kèm kết quả. Nếu có gì sai → sửa, KHÔNG được để nguyên rồi coi như đã xong.

**Việc tiếp theo sau khi chạy thử qua:**
1. Quyết `stock` (Inventory) — có hàng hoá vật lý cần giao hay dịch vụ thuần? Nếu có hàng hoá:
   thêm `stock` vào `depends` của `erp_customize_crm` hoặc module riêng.
2. Nhờ chủ dự án cho biết quy trình bán hàng thật (mấy giai đoạn? tên gì?) để đổi 4 giai đoạn
   mặc định (New/Qualified/Proposition/Won) nếu cần — hiện đang giữ nguyên mặc định của Odoo.
3. Trả lời được thì mới bật Recurring Revenue / Rule-based Assignment (xem mục 5).
4. Bật branch protection cho `develop`/`staging`/`production` trên GitHub web UI (mục 1).

**File cá nhân/bí mật:** `.env` (đã gitignore, chưa tạo — chỉ có `.env.example`). Không có gì
khác cần né trong repo này tính tới giờ.
