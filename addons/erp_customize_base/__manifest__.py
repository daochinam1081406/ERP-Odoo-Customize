# -*- coding: utf-8 -*-
{
    'name': 'ERP Customize — Base',
    'version': '19.0.1.0.0',
    'summary': 'Module khởi điểm cho các tuỳ biến ERP trên nền Odoo 19 Community',
    'category': 'Customizations',
    'author': 'Dao Chi Nam',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/demo_item_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
}
