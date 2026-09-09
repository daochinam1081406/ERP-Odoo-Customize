from . import models


def post_init_hook(env):
    """Bật hai tính năng CÓ SẴN trong Odoo Community nhưng mặc định TẮT.

    Chạy qua Python (post_init_hook), KHÔNG qua XML <record>: các bản ghi
    stage gốc của module `crm` có thể mang noupdate="1" — ghi đè qua XML
    data sẽ bị bỏ qua trong im lặng lúc cài, còn ghi qua ORM thì không.
    """
    # 1) Phễu Lead → Opportunity hai bước, đúng quy ước CRM tiên tiến
    #    (Salesforce Lead object, HubSpot lead lifecycle stage) — mặc
    #    định Odoo bỏ qua bước Lead, đi thẳng vào Opportunity.
    env['res.config.settings'].create({'group_use_lead': True}).execute()

    # 2) Cảnh báo "deal đang thối" (rotting) — Odoo đã có sẵn cơ chế này
    #    trên crm.stage (widget rotting_statusbar_duration ở form Cơ hội)
    #    nhưng ngưỡng mặc định = 0 (tắt) ở MỌI giai đoạn. Số ngày dưới
    #    đây là điểm khởi đầu theo nhịp B2B phổ biến — chỉnh trực tiếp
    #    trên từng giai đoạn (Cấu hình > Giai đoạn) khi có số liệu thật.
    thresholds = {
        'crm.stage_lead1': 7,    # New — quá 1 tuần chưa liên hệ là nguội
        'crm.stage_lead2': 14,   # Qualified — đã xác nhận mà đọng >2 tuần là bất thường
        'crm.stage_lead3': 21,   # Proposition — sau báo giá, im lặng >3 tuần là dấu hiệu xấu
        # Won (stage_lead4): cố ý KHÔNG đặt — deal đã chốt, "thối" vô nghĩa.
    }
    for xml_id, days in thresholds.items():
        stage = env.ref(xml_id, raise_if_not_found=False)
        if stage:
            stage.rotting_threshold_days = days
