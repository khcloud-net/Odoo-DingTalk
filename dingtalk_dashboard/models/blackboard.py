# -*- coding: utf-8 -*-
import json
import logging
import requests
from requests import ReadTimeout
from odoo import api, models

_logger = logging.getLogger(__name__)


class DingTalkBlackboard(models.TransientModel):
    _description = '获取公告信息'
    _name = 'dingtalk.blackboard'

    @api.model
    def get_blackboard_by_user(self):
        """
        根据当前用户获取公告信息
        :return:
        """
        logging.info(">>>开始获取用户{}的公告信息...".format(self.env.user.name))
        uid = self.env.user.id
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', uid)])
        if emp:
            url = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'get_user_blackboard')]).value
            token = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'token')]).value
            data = {
                'userid': emp[0].din_id,
            }
            headers = {'Content-Type': 'application/json'}
            try:
                result = requests.post(url="{}{}".format(url, token), headers=headers, data=json.dumps(data),
                                       timeout=6)
                result = json.loads(result.text)
                if result.get('errcode') == 0:
                    line_list = list()
                    for line in result.get('blackboard_list'):
                        line_list.append(line)
                    return {'state': True, 'data': line_list, 'msg': '', 'number': len(line_list)}
                else:
                    return {'state': False, 'msg': '获取公告失败,详情为:{}'.format(result.get('errmsg'))}
            except ReadTimeout:
                return {'state': False, 'msg': '获取公告网络连接超时'}
            except Exception:
                return {'state': False, 'msg': "获取用户'{}'的公告失败".format(self.env.user.name)}
        logging.info(">>>获取用户公告信息结束...")
