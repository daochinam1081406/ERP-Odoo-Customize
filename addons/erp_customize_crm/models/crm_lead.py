# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmLead(models.Model):
    """Kế thừa crm.lead — hai tuỳ biến:

    1. `referred_by_partner_id` — "Người giới thiệu", chỗ leading CRM cũng
       không có sẵn (UTM chỉ ghi kênh marketing, không ghi người cụ thể).
    2. Tự tạo việc "Liên hệ ngay" khi lead vừa vào hệ thống — xem
       `_schedule_first_contact_activity`.
    """

    _inherit = 'crm.lead'

    referred_by_partner_id = fields.Many2one(
        'res.partner',
        string='Được giới thiệu bởi',
        help='Khách hàng/nhân viên/đối tác đã giới thiệu cơ hội này.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)
        leads._schedule_first_contact_activity()
        return leads

    def _schedule_first_contact_activity(self):
        """Tự tạo việc "Liên hệ ngay" ngay khi lead vào hệ thống.

        KHÔNG phải chi tiết UX — là đòn bẩy chuyển đổi lớn nhất trong bán
        hàng B2B, theo dữ liệu thật (HBR, khảo sát 2.241 công ty Mỹ):
        liên hệ trong GIỜ ĐẦU tăng 7 lần khả năng nói chuyện được người
        quyết định; chờ quá 24 GIỜ thì khả năng đủ điều kiện giảm 60 LẦN;
        78% khách B2B mua của bên phản hồi ĐẦU TIÊN. Hệ thống phải tự
        nhắc — không trông chờ ai nhớ kiểm tra hộp thư.
        """
        for lead in self:
            lead.activity_schedule(
                'mail.mail_activity_data_call',
                date_deadline=fields.Date.context_today(lead),
                summary=(
                    'Liên hệ ngay trong hôm nay — chờ quá 24h giảm 60 lần '
                    'cơ hội đủ điều kiện (khảo sát HBR)'
                ),
                user_id=lead.user_id.id or self.env.user.id,
            )
