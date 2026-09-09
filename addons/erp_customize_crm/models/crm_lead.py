# -*- coding: utf-8 -*-
from odoo import fields, models


class CrmLead(models.Model):
    """Kế thừa crm.lead — thêm 'Người giới thiệu'.

    Đây là khoảng trống thật ngay cả ở các CRM tiên tiến: UTM (Nguồn/Kênh/
    Chiến dịch) chỉ ghi được KÊNH marketing (Google Ads, Website...), không
    ghi được một NGƯỜI cụ thể đã giới thiệu. Trong khi các tính năng khác
    (chấm điểm lead tự động, phát hiện trùng lặp, cảnh báo deal đọng) đã có
    sẵn trong Odoo Community — không viết lại, chỉ cấu hình (xem __init__.py).
    """

    _inherit = 'crm.lead'

    referred_by_partner_id = fields.Many2one(
        'res.partner',
        string='Được giới thiệu bởi',
        help='Khách hàng/nhân viên/đối tác đã giới thiệu cơ hội này.',
    )
