# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmLead(models.Model):
    """Kế thừa crm.lead — thêm chỉ số 'số ngày đọng ở giai đoạn hiện tại',
    thứ CRM gốc không có sẵn nhưng người quản lý bán hàng luôn cần để phát
    hiện thương vụ đang bị bỏ quên trong phễu.
    """

    _inherit = 'crm.lead'

    days_in_stage = fields.Integer(
        string='Số ngày ở giai đoạn hiện tại',
        compute='_compute_days_in_stage',
        help=(
            'Tính từ lần đổi giai đoạn gần nhất (date_last_stage_update). '
            'Không lưu — luôn tính lại theo thời điểm hiện tại.'
        ),
    )

    @api.depends('date_last_stage_update')
    def _compute_days_in_stage(self):
        now = fields.Datetime.now()
        for lead in self:
            if lead.date_last_stage_update:
                lead.days_in_stage = (now - lead.date_last_stage_update).days
            else:
                lead.days_in_stage = 0
