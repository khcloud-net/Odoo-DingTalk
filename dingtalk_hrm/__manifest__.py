# -*- coding: utf-8 -*-
{
    'name': "钉钉办公-智能人事",
    'summary': """钉钉办公-智能人事""",
    'description': """ 智能人事相关的接口需要企业开通了钉钉官方的“智能人事”应用之后才可以调用。您可以在手机端工作台打开应用中心，搜索智能人事，然后开通应用 """,
    'author': "SuXueFeng",
    'website': "https://www.sxfblog.com",
    'category': 'dingtalk',
    'version': '1.0',
    'depends': ['base', 'ali_dingtalk'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'data': [
        'security/hrm_group.xml',
        'security/ir.model.access.csv',
        'data/system_conf.xml',
        'views/menu.xml',
        'views/assets.xml',
        'views/hrm_list.xml',
        'views/hrm_dimission_list.xml',
        'views/add_employee.xml',
    ],
    'qweb': [
         'static/xml/*.xml',
    ],
    'price': '50',
    'currency': 'EUR',
    'images':  ['static/description/app1.png']
}
