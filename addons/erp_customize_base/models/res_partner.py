# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    """Kế thừa model res.partner có sẵn của Odoo Community — KHÔNG sửa
    file gốc. Đây là cách chuẩn để tuỳ biến: `_inherit` thay vì viết đè.
    """

    _inherit = 'res.partner'

    internal_reference = fields.Char(
        string='Mã nội bộ',
        help='Ví dụ trường tuỳ biến, chèn thêm vào model res.partner gốc.',
    )
