# -*- encoding: utf-8 -*-
{
    "name": "钉钉办公-扫码/免密登录模块",
    "version": "2.0",
    "license": "AGPL-3",
    "depends": ["base", "auth_oauth", "base_setup", "ali_dindin"],
    "author": "SuXueFeng, OnGood",
    'website': 'http://www.ongood.cn',
    "category": "Tools",
    "description": """用钉钉账号密码/扫码登陆odoo，应用内免登
    """,
    "data": [
        'data/auth_oauth_data.xml',
        'views/auto_templates.xml',
        'views/auth_oauth_templates.xml',
    ],
    "init_xml": [],
    'update_xml': [],
    'demo_xml': [],
    'images': ['static/description/banner.jpg', 'static/description/main_screenshot.png'],
    'installable': True,
    'active': False,
}
