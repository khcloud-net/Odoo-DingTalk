# -*- coding: utf-8 -*-
{
    'name': "钉钉办公-待办事项管理",
    'summary': """钉钉办公-待办事项管理""",
    'description': """ 钉钉办公-待办事项管理 """,
    'author': "SuXueFeng",
    'website': "https://www.sxfblog.com",
    'category': 'dingtalk',
    'version': '1.0',
    'depends': ['base', 'ali_dingtalk', 'mail'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'data/system_conf.xml',
        'data/record_crom.xml',
        'views/work_record.xml',
    ],
    # 'qweb': [
    #     'static/xml/*.xml'
    # ]

}
