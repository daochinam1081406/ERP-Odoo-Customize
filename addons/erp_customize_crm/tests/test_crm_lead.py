# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCrmLeadCustomizations(TransactionCase):
    """Khoá lại hành vi đã xác nhận chạy thật (10-13/09/2026) — không chỉ
    kiểm code mới viết, mà kiểm CẢ hành vi có sẵn của Odoo mà mình đang
    dựa vào (phân quyền), để một thay đổi vô tình ở đâu đó (thêm ir.rule
    sai, đổi nhóm quyền mặc định, sửa nhầm __init__.py) không lặng lẽ phá
    vỡ mà không ai biết.
    """

    def test_referred_by_partner_id_roundtrip(self):
        referrer = self.env['res.partner'].create({'name': 'Referrer Test'})
        lead = self.env['crm.lead'].create({
            'name': 'Test lead',
            'referred_by_partner_id': referrer.id,
        })
        self.assertEqual(lead.referred_by_partner_id, referrer)

    def test_pipeline_has_six_stages_in_order(self):
        """Pipeline phải đúng 6 giai đoạn, đúng thứ tự — không phải 4 giai
        đoạn mặc định sơ sài của Odoo."""
        stages = self.env['crm.stage'].search([], order='sequence')
        self.assertEqual(stages.mapped('name'), [
            'Lead mới', 'Đã xác nhận nhu cầu', 'Khảo sát yêu cầu',
            'Đã gửi báo giá', 'Đàm phán', 'Chốt thắng',
        ])

    def test_first_stage_has_tightest_rotting_threshold(self):
        """"Lead mới" phải là giai đoạn có ngưỡng đọng CHẶT NHẤT (1 ngày)
        — đúng phát hiện: chờ quá 24h giảm 60 lần khả năng đủ điều kiện
        (HBR, khảo sát 2.241 công ty Mỹ). Đây là con số CÓ CĂN CỨ, không
        phải đoán — test này chống việc ai đó nới lỏng nó mà không biết
        vì sao 1 ngày lại quan trọng."""
        stages_with_threshold = self.env['crm.stage'].search([
            ('rotting_threshold_days', '>', 0),
        ])
        tightest = min(stages_with_threshold, key=lambda s: s.rotting_threshold_days)
        self.assertEqual(tightest.name, 'Lead mới')
        self.assertEqual(tightest.rotting_threshold_days, 1)

    def test_won_stage_has_no_rotting_threshold(self):
        won = self.env.ref('crm.stage_lead4')
        self.assertTrue(won.is_won)
        self.assertEqual(won.rotting_threshold_days, 0)

    def test_create_schedules_first_contact_activity(self):
        """Phần quan trọng nhất của thiết kế: tạo lead mới PHẢI tự sinh
        activity "Gọi ngay" hạn NGAY HÔM NAY — biến số liệu (78% khách
        B2B mua của bên phản hồi đầu tiên) thành hành vi hệ thống, không
        chỉ hiển thị cảnh báo trông chờ ai đó tự nhớ kiểm tra."""
        lead = self.env['crm.lead'].create({'name': 'Speed to lead test'})
        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'crm.lead'),
            ('res_id', '=', lead.id),
        ])
        self.assertEqual(len(activities), 1)
        self.assertEqual(
            activities.activity_type_id,
            self.env.ref('mail.mail_activity_data_call'),
        )
        self.assertEqual(activities.date_deadline, fields.Date.context_today(lead))

    def test_bare_internal_user_has_no_crm_access_by_default(self):
        """Nhân viên nội bộ KHÔNG được gán quyền Sales thì bị chặn tuyệt
        đối, không phải mở nhầm mặc định. Xác nhận chạy thật 13/09/2026."""
        bare_user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Bare user test',
            'login': 'bare_user_test@example.com',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        with self.assertRaises(AccessError):
            self.env['crm.lead'].with_user(bare_user).search([])

    def test_salesperson_cannot_see_colleague_opportunity(self):
        """Chốt kiểm soát bảo mật quan trọng nhất cho một CRM nhiều người
        dùng: nhân viên chỉ có quyền "Own Documents Only" KHÔNG được thấy
        deal của đồng nghiệp. Đây là cơ chế CÓ SẴN của Odoo
        (sales_team.group_sale_salesman + ir.rule "Personal Leads") —
        test này khoá lại để không ai vô tình làm hỏng."""
        own_only_group = self.env.ref('sales_team.group_sale_salesman')
        internal_group = self.env.ref('base.group_user')

        sale_a = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Sale A test',
            'login': 'sale_a_test@example.com',
            'group_ids': [(6, 0, [internal_group.id, own_only_group.id])],
        })
        sale_b = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Sale B test',
            'login': 'sale_b_test@example.com',
            'group_ids': [(6, 0, [internal_group.id, own_only_group.id])],
        })
        lead_b = self.env['crm.lead'].create({
            'name': 'Deal của Sale B',
            'user_id': sale_b.id,
        })

        visible_to_a = self.env['crm.lead'].with_user(sale_a).search([
            ('id', '=', lead_b.id),
        ])
        self.assertFalse(visible_to_a, 'Sale A không được thấy deal của Sale B')

        visible_to_b = self.env['crm.lead'].with_user(sale_b).search([
            ('id', '=', lead_b.id),
        ])
        self.assertEqual(visible_to_b, lead_b, 'Sale B phải thấy deal của chính mình')
