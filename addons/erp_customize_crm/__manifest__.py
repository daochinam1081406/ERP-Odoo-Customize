# -*- coding: utf-8 -*-
{
    'name': 'ERP Customize — CRM',
    'version': '19.0.1.0.0',
    'summary': 'Tuỳ biến trọng tâm hệ thống: CRM + khép vòng sang Sales/Invoicing',
    'category': 'Sales/CRM',
    'author': 'Dao Chi Nam',
    'license': 'LGPL-3',
    # sale_crm là cầu nối chính thức của Odoo: cài nó tự kéo theo `sale`
    # (Quotations/Orders) và `account` (Invoicing) — khép vòng
    # Lead → Opportunity → Quotation → Invoice mà không cần tự viết cầu nối.
    'depends': ['crm', 'sale_crm', 'erp_customize_base'],
    'data': [
        'views/crm_lead_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
}
