# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (C) 2019 SuXueFeng
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import base64
import hashlib
import json
import logging
import time
import requests
from requests import ReadTimeout, ConnectTimeout
from odoo import api, models, fields, _
import hmac
from urllib.parse import quote
from odoo.exceptions import UserError
from dingtalk.client import AppKeyClient
from dingtalk.storage.memorystorage import MemoryStorage

mem_storage = MemoryStorage()
_logger = logging.getLogger(__name__)


class DingDingTools(models.TransientModel):
    _description = '钉钉工具类'
    _name = 'dingding.api.tools'

    @api.model
    def get_client(self):
        """
        返回sdk钉钉客户端
        :return:
        """
        corp_id = self.env['ir.config_parameter'].sudo().get_param('dingding_base.corp_id')
        app_key, app_secret = self._get_key_and_secrect()
        if not app_key or not app_secret or not corp_id:
            raise UserError(_('钉钉设置项中的CorpId、AppKey和AppSecret不能为空'))
        return AppKeyClient(corp_id, app_key, app_secret, storage=mem_storage)

    @api.model
    def _get_key_and_secrect(self):
        """
        获取配置项中钉钉key和app_secret
        :return:
        """
        app_key = self.env['ir.config_parameter'].sudo().get_param('dingding_base.app_key')
        app_secret = self.env['ir.config_parameter'].sudo().get_param('dingding_base.app_secret')
        return app_key, app_secret

    @api.model
    def _get_login_appid_and_key(self):
        """
        返回钉钉登录配置项中的appid和appsecret
        :return:
        """
        login_appid = self.env['ir.config_parameter'].sudo().get_param('dingding_base.din_login_appid')
        login_appsecret = self.env['ir.config_parameter'].sudo().get_param('dingding_base.din_login_appsecret')
        return login_appid, login_appsecret

    @api.model
    def send_get_request(self, url, token, data, timeout=None):
        """
        发送get请求至钉钉api
        :param url:
        :param token:
        :param data:
        :param timeout:
        :return:
        """
        timeout = 3 if not timeout else timeout
        try:
            result = requests.get(url="{}{}".format(url, token), params=data, timeout=timeout)
            result = json.loads(result.text)
            return result
        except Exception as e:
            logging.info(">>>钉钉Exception:{}".format(str(e)))
            return False

    @api.model
    def send_post_request(self, url, token, data, timeout=None):
        """
        发送post请求至钉钉api
        :return:
        """
        headers = {'Content-Type': 'application/json'}
        timeout = 3 if not timeout else timeout
        try:
            result = requests.post(url="{}{}".format(url, token), headers=headers, data=json.dumps(data), timeout=timeout)
            result = json.loads(result.text)
            return result
        except ReadTimeout:
            logging.info(">>>钉钉Exception: 网络连接超时！")
            raise UserError("钉钉Exception: 网络连接超时！")
        except ConnectTimeout:
            logging.info(">>>钉钉Exception: 网络连接超时！")
            raise UserError("钉钉Exception: 网络连接超时！")

    @api.model
    def get_time_stamp(self, time_num):
        """
        将13位时间戳转换为时间(utc=0)
        :param time_num:
        :return: "%Y-%m-%d %H:%M:%S"
        """
        time_stamp = float(time_num / 1000)
        time_array = time.gmtime(time_stamp)
        return time.strftime("%Y-%m-%d %H:%M:%S", time_array)

    @api.model
    def timestamp_to_local_date(self, timeNum):
        """
        将13位毫秒时间戳转换为本地日期(+8h)
        :param timeNum:
        :return:
        """
        to_second_timestamp = float(timeNum / 1000)  # 毫秒转秒
        to_utc_datetime = time.gmtime(to_second_timestamp)  # 将时间戳转换为UTC时区（0时区）的时间元组struct_time
        to_str_datetime = time.strftime("%Y-%m-%d %H:%M:%S", to_utc_datetime)  # 将时间元组转成指定格式日期字符串
        to_datetime = fields.Datetime.from_string(to_str_datetime)  # 将字符串转成datetime对象
        to_local_datetime = fields.Datetime.context_timestamp(self, to_datetime)  # 将原生的datetime值(无时区)转换为具体时区的datetime
        to_str_datetime = fields.Datetime.to_string(to_local_datetime)  # datetime 转成 字符串
        return to_str_datetime

    @api.model
    def datetime_to_stamp(self, date):
        """
        将时间转成13位时间戳
        :param time_num:
        :return:
        """
        date_str = fields.Datetime.to_string(date)
        date_stamp = time.mktime(time.strptime(date_str, "%Y-%m-%d %H:%M:%S"))
        date_stamp = date_stamp * 1000
        return date_stamp

    @api.model
    def get_token(self):
        """
        获取钉钉token值
        :return:
        """
        app_key, app_secret = self._get_key_and_secrect()
        token_url = self.env['dingding.parameter'].get_parameter_value('token_url')
        data = {'appkey': app_key, 'appsecret': app_secret}
        # 发送数据
        result = requests.get(url=token_url, params=data, timeout=1)
        result = json.loads(result.text)
        logging.info(">>>钉钉Token:{}".format(result))
        if result.get('errcode') == 0:
            token = self.env['dingding.parameter'].search([('key', '=', 'token')])
            if token:
                token.write({'value': result.get('access_token')})
        else:
            logging.info(">>>获取钉钉Token失败！请检查网络是否通畅或检查日志输出!")

    @api.model
    def get_userid_by_unionid(self, unionid):
        """
        根据unionid获取userid
        :param unionid:
        :return:
        """
        url, token = self.env['dingding.parameter'].sudo().get_parameter_value_and_token('getUseridByUnionid')
        data = {'unionid': unionid}
        result = requests.get(url="{}{}".format(url, token), params=data, timeout=2)
        logging.info(">>>根据unionid获取userid获取结果:{}".format(result.text))
        result = json.loads(result.text)
        if result.get('errcode') == 0:
            return result.get('userid')
        else:
            logging.info(">>>根据unionid获取userid获取结果失败，原因为:{}".format(result.get('errmsg')))

    @api.model
    def get_user_info_by_code(self, code):
        """
        用于在钉钉登录时根据返回的临时授权码获取用户信息
        :param code:
        :return:
        """
        url = self.env['dingding.parameter'].sudo().get_parameter_value('getuserinfo_bycode')
        login_appid, key = self._get_login_appid_and_key()
        current_milli_time = lambda: int(round(time.time() * 1000))
        msg = str(current_milli_time())
        signature = hmac.new(key.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).digest()
        signature = quote(base64.b64encode(signature), 'utf-8')
        data = {'tmp_auth_code': code}
        headers = {'Content-Type': 'application/json'}
        new_url = "{}signature={}&timestamp={}&accessKey={}".format(url, signature, msg, login_appid)
        try:
            result = requests.post(url=new_url, headers=headers, data=json.dumps(data), timeout=2)
            result = json.loads(result.text)
            logging.info(">>>钉钉登录获取用户信息返回结果{}".format(result))
            if result.get('errcode') == 0:
                user_info = result.get('user_info')
                employee = self.env['hr.employee'].sudo().search([('din_unionid', '=', user_info.get('unionid'))])
                if employee:
                    return {'state': True, 'employee': employee}
                else:
                    return {'state': False, 'msg': "钉钉员工'{}'在系统中不存在,请联系管理员维护!".format(user_info.get('nick'))}
            else:
                return {'state': False, 'msg': '钉钉登录获取用户信息失败，详情为:{}'.format(result.get('errmsg'))}
        except ReadTimeout:
            return {'state': False, 'msg': '网络连接超时'}

    @api.model
    def send_work_message(self, msg, user_id):
        """
        发送工作通知消息到指定员工
        :param msg:
        :param user_id:
        :return:
        """
        try:
            agent_id = self.env['ir.config_parameter'].sudo().get_param('dingding_base.agent_id')
            url, token = self.env['dingding.parameter'].sudo().get_parameter_value_and_token('send_work_message')
            data = {
                'agent_id': agent_id,
                'userid_list': user_id,
                'msg': msg,
            }
            result = self.send_post_request(url, token, data)
            return True
        except Exception as e:
            return False
