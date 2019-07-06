# -*- coding: utf-8 -*-
import json
import logging
import requests
from requests import ReadTimeout
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.modules import get_module_resource
from odoo.addons.ali_dindin.models.dingtalk_client import get_client
from odoo import tools
import base64
_logger = logging.getLogger(__name__)


class DingDingChat(models.Model):
    _name = 'dingding.chat'
    _description = "钉钉群会话"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('dindin_message', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    chat_id = fields.Char(string='群会话Id')
    chat_icon = fields.Char(string='群头像mediaId')
    name = fields.Char(string='群名称', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string=u'公司',
                                 default=lambda self: self.env.user.company_id.id)
    employee_id = fields.Many2one(comodel_name='hr.employee', string=u'群主', required=True)
    show_history_type = fields.Selection(string=u'聊天历史消息', selection=[(0, '否'), (1, '是'), ], default=0,
                                         help="新成员是否可查看聊天历史消息,新成员入群是否可查看最近100条聊天记录")
    searchable = fields.Selection(string=u'群可搜索', selection=[(0, '否'), (1, '是'), ], default=0)
    validation_type = fields.Selection(string=u'入群验证', selection=[(0, '否'), (1, '是'), ], default=0)
    mention_all_authority = fields.Selection(string=u'@all 权限', selection=[(0, '所有人'), (1, '仅群主'), ], default=0)
    chat_banned_type = fields.Selection(string=u'群禁言', selection=[(0, '不禁言'), (1, '全员禁言'), ], default=0)
    management_ype = fields.Selection(string=u'管理类型', selection=[(0, '所有人可管理'), (1, '仅群主可管理')], default=1)
    useridlist = fields.Many2many(comodel_name='hr.employee', relation='dingding_chat_and_hr_employee_rel',
                                  column1='chat_id', column2='emp_id', string=u'群成员', required=True)
    state = fields.Selection(string=u'状态', selection=[('new', '新建'), ('normal', '已建立'), ('close', '解散')],
                             default='new', track_visibility='onchange')
    channel_ids = fields.Many2many(comodel_name='mail.channel', relation='dingding_chat_and_mail_channel_rel',
                                   column1='chat_id', column2='mail_id', string=u'关注频道')
    model_ids = fields.Many2many(comodel_name='ir.model', relation='dingding_chat_and_ir_model_rel',
                                 column1='chat_id', column2='model_id', string=u'关联模型')
    image = fields.Binary("照片", default=_default_image, attachment=True)
    image_medium = fields.Binary("Medium-sized photo", attachment=True)
    image_small = fields.Binary("Small-sized photo", attachment=True)
    robot_count = fields.Integer(string=u'群机器人数', compute='get_robot_count')
    active = fields.Boolean(default=True)

    @api.model
    def create(self, values):
        tools.image_resize_images(values)
        return super(DingDingChat, self).create(values)

    @api.multi
    def write(self, values):
        tools.image_resize_images(values)
        return super(DingDingChat, self).write(values)

    @api.multi
    def get_robot_count(self):
        """
        获取当前群的群机器人数量
        :return:
        """
        for res in self:
            res.robot_count = self.env['dingding.robot'].search_count([('chat_id', '=', res.id)])

    @api.multi
    def action_view_robot(self):
        """
        跳转到群机器人列表
        :return:
        """
        self.ensure_one()
        action = self.env.ref('dindin_message.dingding_robot_action').read()[0]
        action['domain'] = [('chat_id', '=', self.id)]
        return action

    @api.multi
    def create_dingding_chat(self):
        """
        创建会话

        :param name: 群名称。长度限制为1~20个字符
        :param owner: 群主userId，员工唯一标识ID；必须为该会话useridlist的成员之一
        :param useridlist: 群成员列表，每次最多支持40人，群人数上限为1000
        :param show_history_type: 新成员是否可查看聊天历史消息（新成员入群是否可查看最近100条聊天记录）
        :param searchable: 群可搜索，0-默认，不可搜索，1-可搜索
        :param validation_type: 入群验证，0：不入群验证（默认） 1：入群验证
        :param mention_all_authority: @all 权限，0-默认，所有人，1-仅群主可@all
        :param chat_banned_type: 群禁言，0-默认，不禁言，1-全员禁言
        :param management_type: 管理类型，0-默认，所有人可管理，1-仅群主可管理
        :return: 群会话的id
        """
        for res in self:
            user_list = self.check_employee_din_id(res)
            logging.info(">>>开始钉钉创建群会话")
            name=res.name
            owner=res.employee_id.din_id
            showHistoryType=res.show_history_type
            searchable=res.searchable
            validationType=res.validation_type
            mentionAllAuthority=res.mention_all_authority
            chatBannedType=res.chat_banned_type
            managementType=res.management_ype
            useridlist=user_list
            try:
                client = get_client(self)
                result = client.chat.create(name, owner, useridlist, show_history_type=showHistoryType, searchable=searchable,
                    validation_type=validationType, mention_all_authority=mentionAllAuthority, chat_banned_type=chatBannedType, management_type=managementType)
                logging.info(">>>创建会话返回结果{}".format(result)) 
                if result.get('errcode') == 0:
                    res.write({'chat_id': result.get('chatid'), 'state': 'normal'})
                    res.message_post(body=u"群会话已创建!群会话的ID:{}".format(result.get('chatid')), message_type='notification')
                else:
                    raise UserError('创建失败，详情为:{}'.format(result.get('errmsg')))
            except Exception as e:
                raise UserError(e)

    @api.multi
    def write_dingding_chat(self):
        """
        修改会话

        :param chatid: 群会话的id
        :param name: 群名称。长度限制为1~20个字符，不传则不修改
        :param owner: 群主userId，员工唯一标识ID；必须为该会话成员之一；不传则不修改
        :param add_useridlist: 添加成员列表，每次最多支持40人，群人数上限为1000
        :param del_useridlist: 删除成员列表，每次最多支持40人，群人数上限为1000
        :param icon: 群头像mediaid
        :param chat_banned_type: 群禁言，0-默认，不禁言，1-全员禁言
        :param searchable: 群可搜索，0-默认，不可搜索，1-可搜索
        :param validation_type: 入群验证，0：不入群验证（默认） 1：入群验证
        :param mention_all_authority: @all 权限，0-默认，所有人，1-仅群主可@all
        :param show_history_type: 新成员是否可查看聊天历史消息（新成员入群是否可查看最近100条聊天记录）
        :param management_type: 管理类型，0-默认，所有人可管理，1-仅群主可管理
        :return:
        """
        for res in self:
            self.check_employee_din_id(res)
            logging.info(">>>开始钉钉修改群会话")

            chatid = res.chat_id
            name = res.name
            owner = res.employee_id.din_id
            showHistoryType = res.show_history_type
            searchable = res.searchable
            validationType = res.validation_type
            mentionAllAuthority = res.mention_all_authority
            chatBannedType = res.chat_banned_type
            managementType = res.management_ype

            try:
                client = get_client(self)
                result = client.chat.update(chatid, name=name, owner=owner, add_useridlist=(), del_useridlist=(), icon='', chat_banned_type=chatBannedType,
                    searchable=searchable, validation_type=validationType, mention_all_authority=mentionAllAuthority, show_history_type=showHistoryType, management_type=managementType)
                logging.info(">>>修改会话返回结果{}".format(result)) 
                if result.get('errcode') == 0:
                    res.message_post(body=u"群会话已修改!", message_type='notification')
                else:
                    raise UserError('修改失败，详情为:{}'.format(result.get('errmsg')))
            except Exception as e:
                raise UserError(e)

    @api.model
    def check_employee_din_id(self, res):
        if not res.employee_id.din_id:
            raise UserError("员工（群主）在钉钉中不存在，请选择其他人员!")
        user_list = list()
        for emp in res.useridlist:
            if not emp.din_id:
                raise UserError("员工{}:在钉钉中不存在，请选择其他人员!".format(emp.name))
            user_list.append(emp.din_id)
        return user_list

    @api.model
    def process_dingding_chat_onchange(self, msg):
        """
        处理回调
        :param msg: msg
        :return:
        """
        print(msg)
        chat = self.env['dingding.chat'].sudo().search([('chat_id', '=', msg.get('ChatId'))])
        # 群会话更换群主
        if msg.get('EventType') == 'chat_update_owner':
            if chat:
                employee = self.env['hr.employee'].sudo().search([('din_id', '=', msg.get('Owner'))])
                if employee:
                    chat.sudo().write({'employee_id': employee[0].id})
        # 群会话更换群名称
        elif msg.get('EventType') == 'chat_update_title':
            if chat:
                chat.sudo().write({'name': msg.get('Title')})
        # 群会话添加人员
        elif msg.get('EventType') == 'chat_add_member':
            new_users = list()
            for user in chat.useridlist:
                new_users.append(user.id)
            for user in msg.get('UserId'):
                employee = self.env['hr.employee'].sudo().search([('din_id', '=', user)])
                if employee:
                    new_users.append(employee[0].id)
            chat.sudo().write({'useridlist': [(6, 0, new_users)]})
        # 群会话删除人员
        elif msg.get('EventType') == 'chat_remove_member':
            for user in msg.get('UserId'):
                employee = self.env['hr.employee'].sudo().search([('din_id', '=', user)])
                if employee:
                    chat.sudo().write({'useridlist': [(3, employee[0].id)]})
        # 群会话用户主动退群
        elif msg.get('EventType') == 'chat_quit':
            employee = self.env['hr.employee'].sudo().search([('din_id', '=', msg.get('Operator'))])
            if employee:
                chat.sudo().write({'useridlist': [(3, employee[0].id)]})
        # 群会话解散群
        elif msg.get('EventType') == 'chat_disband':
            if chat:
                emp = self.env['hr.employee'].sudo().search([('din_id', '=', msg.get('Operator'))])
                chat.sudo().write({'state': 'close'})
                if emp:
                    chat.sudo().message_post(body=u"群会话已被解散，操作人: {}!".format(emp[0].name), message_type='notification')
        return True


class DingDingChatUserModelAdd(models.TransientModel):
    _name = 'dingding.chat.user.model.add'
    _description = "群会话添加成员"

    on_user_ids = fields.Many2many(comodel_name='hr.employee', relation='dingding_chat_on_user_add_and_hr_employee_rel',
                                   column1='model_id', column2='emp_id', string=u'已有成员')
    user_ids = fields.Many2many(comodel_name='hr.employee', relation='dingding_chat_user_add_and_hr_employee_rel',
                                column1='model_id', column2='emp_id', string=u'新群成员', required=True)

    @api.onchange('on_user_ids')
    def _onchange_on_user_ids(self):
        """待添加人员下拉列表不显示当前群内成员
        """
        if self.on_user_ids:
            domain = [('id','not in', self.on_user_ids.ids)]
            return {
            'domain': {'user_ids': domain}
            }

    @api.model
    def default_get(self, fields):
        res = super(DingDingChatUserModelAdd, self).default_get(fields)
        chat_id = self.env.context.get('active_id', False)
        ding_chat = self.env['dingding.chat'].browse(chat_id)
        if 'on_user_ids' in fields:
            res.update({'on_user_ids': [(6, 0, ding_chat.useridlist.ids)]})
        return res

    @api.multi
    def add_chat_users(self):
        """
        添加群成员
        :return:
        """
        for res in self:
            chat_id = self.env.context.get('active_id', False)
            ding_chat = self.env['dingding.chat'].browse(chat_id)
            user_list = list()
            for emp in res.user_ids:
                if not emp.din_id:
                    raise UserError("员工{}:在钉钉中不存在，请选择其他人员!".format(emp.name))
                user_list.append(emp.din_id)
            chatid = ding_chat.chat_id
            add_useridlist = user_list
            try:
                client = get_client(self)
                result = client.chat.update(chatid, add_useridlist=add_useridlist)
                logging.info(">>>添加群成员返回结果{}".format(result)) 
                if result.get('errcode') == 0:
                    new_user_list = list()
                    for user in res.on_user_ids:
                        new_user_list.append(user.id)
                    for user in res.user_ids:
                        new_user_list.append(user.id)
                    ding_chat.write({'useridlist': [(6, 0, new_user_list)]})
                    ding_chat.message_post(body=u"群成员已增加!", message_type='notification')
                else:
                    raise UserError('群成员更新失败，详情为:{}'.format(result.get('errmsg')))
            except Exception as e:
                raise UserError(e)



class DingDingChatUserModelDel(models.TransientModel):
    _name = 'dingding.chat.user.model.del'
    _description = "群会话删除成员"

    user_ids = fields.Many2many(comodel_name='hr.employee', relation='dingding_chat_user_del_and_hr_employee_rel',
                                column1='model_id', column2='emp_id', string=u'删除群成员', required=True)
    old_user_ids = fields.Many2many(comodel_name='hr.employee',
                                    relation='dingding_chat_old_user_del_and_hr_employee_rel',
                                    column1='model_id', column2='emp_id', string=u'群成员', required=True)

    @api.onchange('old_user_ids')
    def _onchange_old_user_ids(self):
        """待删除人员下拉列表只显示当前群内成员
        """
        if self.old_user_ids:
            domain = [('id','in', self.old_user_ids.ids)]
            return {
            'domain': {'user_ids': domain}
            }

    @api.model
    def default_get(self, fields):
        res = super(DingDingChatUserModelDel, self).default_get(fields)
        chat_id = self.env.context.get('active_id', False)
        ding_chat = self.env['dingding.chat'].browse(chat_id)
        if 'old_user_ids' in fields:
            res.update({'old_user_ids': [(6, 0, ding_chat.useridlist.ids)]})
        return res

    @api.multi
    def del_chat_users(self):
        """
        删除群成员
        :return:
        """
        for res in self:
            chat_id = self.env.context.get('active_id', False)
            ding_chat = self.env['dingding.chat'].browse(chat_id)
            user_list = list()
            for emp in res.user_ids:
                if not emp.din_id:
                    raise UserError("员工{}:在钉钉中不存在，请选择其他人员!".format(emp.name))
                user_list.append(emp.din_id)
            chatid = ding_chat.chat_id
            del_useridlist = user_list
            try:
                client = get_client(self)
                result = client.chat.update(chatid, del_useridlist=del_useridlist)
                logging.info(">>>删除群成员返回结果{}".format(result))
                if result.get('errcode') == 0:
                    for user in res.user_ids:
                        ding_chat.write({'useridlist': [(3, user.id)]})
                    ding_chat.message_post(body=u"群成员已删除!", message_type='notification')
                else:
                    raise UserError('群成员更新失败，详情为:{}'.format(result.get('errmsg')))
            except Exception as e:
                raise UserError(e)


class DingDingSendChatMessage(models.TransientModel):
    _name = 'dingding.send.chat.message'
    _description = "发送群消息"

    message = fields.Text(string=u'消息内容', required=True)

    @api.multi
    def send_dingding_test_message(self):
        """
        点击群会话发送群消息按钮
        :return:
        """
        chat_id = self.env.context.get('active_id', False)
        ding_chat = self.env['dingding.chat'].browse(chat_id)
        chatid = ding_chat.chat_id
        msg = {
            "msgtype": "text",
            "text": {
                "content": self.message
            }
        }
        try:
            client = get_client(self)
            result = client.chat.send(chatid, msg)
            logging.info(">>>发送群消息返回结果{}".format(result))
            if result.get('errcode') == 0:
                ding_chat.message_post(body="消息已成功发送!".format(self.message), message_type='notification')
            else:
                raise UserError('操作失败，详情为:{}'.format(result.get('errmsg')))
        except Exception as e:
            raise UserError(e)

    @api.model
    def send_message(self, ding_chat, body):
        """
        发送群会话消息
        :return:
        """

        chatid = ding_chat.chat_id
        msg = {
            "msgtype": "markdown",
            "markdown": {
                "title": "来自ERP的备注消息",
                "text": body
            }
        }
        try:
            client = get_client(self)
            result = client.chat.send(chatid, msg)
            logging.info(">>>发送群消息返回结果{}".format(result))
        except Exception as e:
            raise UserError(e)
        return True

    @api.model
    def send_work_message(self, userstr, message):
        """
        发送工作消息到指定员工列表
        :param userstr 员工列表  string
        :param message 消息内容
        :return:
        """
        agentid = self.env['ir.config_parameter'].sudo().get_param('ali_dindin.din_agentid')
        userid_list = userstr
        msg_body = {
            "msgtype": "markdown",
            "markdown": {
                "title": "来自ERP的消息",
                "text": message
            }
        }
        try:
            client = get_client(self)
            result = client.message.send(agentid, msg_body, touser_list=userid_list, toparty_list=())
            logging.info(">>>发送待办消息返回结果{}".format(result))
        except Exception as e:
            raise UserError(e)
        return True


class DingDingChatList(models.TransientModel):
    _name = 'get.dingding.chat.list'
    _description = "获取已存在的群会话"

    chat_id = fields.Char(string='群会话Id', required=True)

    @api.multi
    def get_chat_info(self):
        """
        获取群会话
        :return:
        """
        for res in self:
            logging.info(">>>开始获取群会话...")
            chatid = res.chat_id
            try:
                client = get_client(self)
                result = client.chat.get(chatid)
                logging.info(">>>获取群会话返回结果{}".format(result))
                if result.get('errcode') == 0:
                    chat_info = result.get('chat_info')
                    employee = self.env['hr.employee'].sudo().search([('din_id', '=', chat_info.get('owner'))])
                    if not employee:
                        raise UserError("返回的群管理员在Odoo系统中不存在!")
                    user_list = list()
                    for userlist in chat_info.get('useridlist'):
                        user = self.env['hr.employee'].sudo().search([('din_id', '=', userlist)])
                        if user:
                            user_list.append(user[0].id)
                    data = {
                        'chat_id': chat_info.get('chatid'),
                        'chat_icon': chat_info.get('icon'),
                        'name': chat_info.get('name'),
                        'employee_id': employee[0].id,
                        'show_history_type': chat_info.get('showHistoryType'),
                        'searchable': chat_info.get('searchable'),
                        'validation_type': chat_info.get('validationType'),
                        'mention_all_authority': chat_info.get('mentionAllAuthority'),
                        'management_ype': chat_info.get('managementType'),
                        'useridlist': [(6, 0, user_list)],
                        'state': 'normal'
                    }
                    chat = self.env['dingding.chat'].sudo().search([('chat_id', '=', res.chat_id)])
                    if chat:
                        chat.write(data)
                    else:
                        self.env['dingding.chat'].sudo().create(data)
                else:
                    raise UserError('操作失败:{}'.format(result.get('errmsg')))
            except Exception as e:
                raise UserError(e)
