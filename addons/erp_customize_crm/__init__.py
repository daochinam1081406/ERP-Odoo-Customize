from . import models


def post_init_hook(env):
    """Bật tính năng CÓ SẴN nhưng TẮT + thiết kế lại pipeline theo dữ liệu
    B2B thật (không phải mặc định sơ sài của Odoo).

    Chạy qua Python (post_init_hook), KHÔNG qua XML <record> cho các bản
    ghi thuộc module `crm`: chúng có thể mang noupdate="1" — ghi đè qua
    XML data sẽ bị bỏ qua trong im lặng lúc cài, còn ghi qua ORM thì không.
    """
    # 1) Phễu Lead → Opportunity hai bước, đúng quy ước CRM tiên tiến
    #    (Salesforce Lead object, HubSpot lead lifecycle stage).
    env['res.config.settings'].create({'group_use_lead': True}).execute()

    # 2) Đổi tên + tiêu chí thoát (requirements) + ngưỡng "đọng" cho 4 giai
    #    đoạn GỐC của Odoo — thay vì tên tiếng Anh chung chung và ngưỡng
    #    rotting = 0 (tắt) ở mọi nơi.
    #
    #    Số liệu tra được TRƯỚC khi định ngưỡng (không đoán):
    #    - HBR khảo sát 2.241 công ty Mỹ: liên hệ trong GIỜ ĐẦU tăng 7 lần
    #      khả năng nói chuyện được người quyết định
    #    - Chờ quá 24 GIỜ: khả năng đủ điều kiện (qualify) giảm 60 LẦN —
    #      gần như về 0 ở thị trường cạnh tranh
    #    - 78% khách B2B mua của bên phản hồi ĐẦU TIÊN
    #    → "Lead mới" phải là giai đoạn có ngưỡng đọng CHẶT NHẤT (1 ngày),
    #    không phải 7 ngày như bản nháp trước — đó là đoán, không phải số
    #    dựa trên dữ liệu.
    stage_updates = {
        'crm.stage_lead1': {
            'name': 'Lead mới',
            'sequence': 1,
            'requirements': (
                'Đã liên hệ được và xác nhận có quan tâm ban đầu — '
                'TRONG VÒNG 24 GIỜ (chờ quá 24h giảm 60 lần khả năng '
                'đủ điều kiện — HBR, khảo sát 2.241 công ty Mỹ).'
            ),
            'rotting_threshold_days': 1,
        },
        'crm.stage_lead2': {
            'name': 'Đã xác nhận nhu cầu',
            'sequence': 2,
            'requirements': (
                'Đã xác nhận: nhu cầu/vấn đề thật của khách, khoảng '
                'ngân sách, và ai là người quyết định.'
            ),
            'rotting_threshold_days': 10,
        },
        'crm.stage_lead3': {
            'name': 'Đã gửi báo giá',
            'sequence': 4,  # nhường sequence=3 cho "Khảo sát yêu cầu" (data/crm_stage_data.xml)
            'requirements': (
                'Khách đã xác nhận nhận được báo giá và đang đánh giá '
                'theo đúng tiêu chí đã thống nhất.'
            ),
            'rotting_threshold_days': 14,
        },
        'crm.stage_lead4': {
            'name': 'Chốt thắng',
            # sequence giữ nguyên 70 (đứng cuối), rotting giữ 0 — deal đã
            # chốt thì khái niệm "đọng" vô nghĩa.
        },
    }
    for xml_id, vals in stage_updates.items():
        stage = env.ref(xml_id, raise_if_not_found=False)
        if stage:
            stage.write(vals)
