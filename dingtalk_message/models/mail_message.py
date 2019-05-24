# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        message = super(MailMessage, self).create(values)
        # print(values)
        template = self.env['dingtalk.message.template'].sudo()
        model = self.env['ir.model'].sudo().search([('model', '=', values.get('model'))])
        result = template.get_template_by_model_and_type(model, values.get('message_type'))
        if result and result.chat_id:
            if values.get('message_type') == 'comment':
                base_url = "{}/dingtalk/auto/login/in".format(self.env["ir.config_parameter"].get_param("web.base.url"))
                partner = self.env['res.partner'].sudo().search([('id', '=', values.get('author_id'))])
                msg = "*{}*在**{}**备注: \n  - **单据**:{} \n - **内容**:{}  \n  \n [登录ERP]({})".format(
                    partner.name, model.name, values.get('record_name'), values.get('body'), base_url)
                self.env['dingtalk.send.chat.message'].sudo().send_message(result.chat_id, msg)
        return message


class DingTalkMessageTemplate(models.Model):
    _name = 'dingtalk.message.template'
    _description = "钉钉消息模板"
    _rec_name = 'name'

    name = fields.Char(string='消息名称', required=True)
    model_id = fields.Many2one(comodel_name='ir.model', string=u'应用模型', required=True)
    subject = fields.Char(string='消息主题')
    body = fields.Text(string=u'内容')
    active = fields.Boolean(default=True)
    email = fields.Boolean(string=u'Email消息时触发')
    comment = fields.Boolean(string=u'备注消息时触发')
    notification = fields.Boolean(string=u'讨论消息时触发')
    chat_id = fields.Many2one(comodel_name='dingtalk.chat', string=u'To群会话')

    @api.model
    def generate_message_text(self, model_name, body_html, res_id):
        """
        根据Mako语法生成消息文本
        :param model_name: 模型
        :param body_html:内容
        :param res_id: 单据id
        :return:
        """
        result = self.env['mail.template'].sudo()._render_template(body_html, model_name, res_id)
        return result

    @api.model
    def get_template_by_model_and_type(self, model, msh_type):
        if model:
            template = self.env['dingtalk.message.template'].sudo().search(
                [('model_id', '=', model.id), (msh_type, '=', True), ('active', '=', True)])
            return template[0] if template else False