# -*- coding: utf-8 -*-
{
    'name': 'ERP Customize — Base',
    'version': '19.0.1.0.0',
    'summary': 'Nền dùng chung cho mọi tuỳ biến — mở rộng danh bạ (res.partner)',
    'category': 'Customizations',
    'author': 'Dao Chi Nam',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
}
