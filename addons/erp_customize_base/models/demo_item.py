# -*- coding: utf-8 -*-
from odoo import fields, models


class DemoItem(models.Model):
    """Bản ghi khởi điểm — xoá/đổi tên khi bắt đầu module thật."""

    _name = 'erp.customize.demo.item'
    _description = 'ERP Customize Demo Item'
    _order = 'name'

    name = fields.Char(string='Tên', required=True)
    note = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Đang dùng', default=True)
