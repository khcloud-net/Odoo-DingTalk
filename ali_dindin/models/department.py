# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import api, fields, models
from odoo.exceptions import UserError
from .dingtalk_client import get_client
from dingtalk.core.exceptions import DingTalkClientException

_logger = logging.getLogger(__name__)

""" 钉钉部门功能模块 """


# 拓展部门
class HrDepartment(models.Model):
    _inherit = 'hr.department'

    din_id = fields.Char(string='钉钉Id')
    din_sy_state = fields.Boolean(string=u'钉钉同步标识', default=False, help="避免使用同步时,会执行创建、修改上传钉钉方法")
    dingding_type = fields.Selection(string=u'钉钉状态', selection=[('no', '不存在'), ('yes', '存在')],
                                     compute="_compute_dingding_type")

    @api.multi
    def create_ding_department(self):
        
        for res in self:
            if res.din_id:
                raise UserError("该部门已在钉钉中存在！")
            data = {
                'name': res.name,  # 部门名称
            }
            # 获取父部门din_id
            if res.parent_id:
                data.update({'parentid': res.parent_id.din_id if res.parent_id.din_id else ''})
            else:
                raise UserError("请选择上级部门!")
            try:
                client = get_client(self)
                result = client.department.create(data)              
                logging.info(">>>新增部门返回结果:{}".format(result))
                if result.get('errcode') == 0:
                    res.write({'din_id': result.get('id')})
                    res.message_post(body=u"钉钉消息：部门信息已上传至钉钉", message_type='notification')
                else:
                    raise UserError('上传钉钉系统时发生错误，详情为:{}'.format(result.get('errmsg')))
            except DingTalkClientException as e:
                raise UserError(e)

    @api.multi
    def update_ding_department(self):

        for res in self:
            # 获取部门din_id
            if not res.parent_id:
                raise UserError("请选择上级部门!")
            data = {
                'id': res.din_id,  # id
                'name': res.name,  # 部门名称
                'parentid': res.parent_id.din_id,  # 父部门id
            }
            try:
                client = get_client(self)
                result = client.department.update(data)    
                logging.info(">>>修改部门时钉钉返回结果:{}".format(result))
                if result.get('errcode') == 0:
                    res.message_post(body=u"钉钉消息：新的信息已同步更新至钉钉", message_type='notification')
                else:
                    raise UserError('上传钉钉系统时发生错误，详情为:{}'.format(result.get('errmsg')))
            except DingTalkClientException as e:
                raise UserError(e)

    # 重写删除方法
    @api.multi
    def unlink(self):

        for res in self:
            din_id = res.din_id
            super(HrDepartment, self).unlink()
            din_delete_department = self.env['ir.config_parameter'].sudo().get_param('ali_dindin.din_delete_department')
            if din_delete_department:
                self.delete_din_department(din_id)
            return True

    @api.model
    def delete_din_department(self, din_id):
        """删除钉钉部门"""
        try:
            client = get_client(self)
            result = client.department.delete(din_id)    
            logging.info(">>>删除钉钉部门返回结果:{}".format(result))
            if result.get('errcode') != 0:
                raise UserError('删除钉钉部门时发生错误，详情为:{}'.format(result.get('errmsg')))
        except DingTalkClientException as e:
            raise UserError(e)

    def _compute_dingding_type(self):
        for res in self:
            res.dingding_type = 'yes' if res.din_id else 'no'


# 未使用，但是不能删除，因为第一个版本创建的视图还存在
class DinDinSynchronousDepartment(models.TransientModel):
    _name = 'dindin.synchronous.department'
    _description = "同步钉钉部门功能模型"
