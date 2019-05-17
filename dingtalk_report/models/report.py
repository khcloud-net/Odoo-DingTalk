# -*- coding: utf-8 -*-
import json
import logging
import requests
import time
from requests import ReadTimeout
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DingtalkReportTemplate(models.Model):
    _name = 'dingtalk.report.template'
    _description = "日志模板"
    _rec_name = 'name'

    name = fields.Char(string='模板名', required=True)
    icon_url = fields.Char(string='图标url')
    report_code = fields.Char(string='模板唯一标识')
    url = fields.Char(string='模板跳转url')
    company_id = fields.Many2one(comodel_name='res.company',
                                 string=u'公司', default=lambda self: self.env.user.company_id.id)

    @api.model
    def get_template(self):
        """获取日志模板"""
        logging.info(">>>获取日志模板...")
        url = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'get_report_template_listbyuserid')]).value
        token = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'token')]).value
        data = {
            'offset': 0,
            'size': 100,
        }
        headers = {'Content-Type': 'application/json'}
        try:
            result = requests.post(url="{}{}".format(url, token), headers=headers, data=json.dumps(data), timeout=20)
            result = json.loads(result.text)
            # logging.info(">>>获取日志模板返回结果{}".format(result))
            if result.get('errcode') == 0:
                d_res = result.get('result')
                for report in d_res.get('template_list'):
                    data = {
                        'name': report.get('name'),
                        'icon_url': report.get('icon_url'),
                        'report_code': report.get('report_code'),
                        'url': report.get('url'),
                    }
                    template = self.env['dingtalk.report.template'].search(
                        [('report_code', '=', report.get('report_code'))])
                    if template:
                        template.write(data)
                    else:
                        self.env['dingtalk.report.template'].create(data)
            else:
                raise UserError('获取日志模板失败，详情为:{}'.format(result.get('errmsg')))
        except ReadTimeout:
            raise UserError("网络连接超时！")
        logging.info(">>>获取日志模板结束...")

    @api.model
    def get_get_template_number_by_user(self):
        """
        根据当前用户获取该用户的未读日志数量
        :return:
        """
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if len(emp) > 1:
            return {'state': False, 'number': 0, 'msg': '登录用户关联了多个员工'}
        if emp and emp.din_id:
            url = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'get_report_unreadcount')]).value
            token = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'token')]).value
            data = {
                'userid': emp.din_id,
            }
            headers = {'Content-Type': 'application/json'}
            try:
                result = requests.post(url="{}{}".format(url, token), headers=headers, data=json.dumps(data), timeout=5)
                result = json.loads(result.text)
                if result.get('errcode') == 0:
                    return {'state': True, 'number': result.get('count')}
                else:
                    return {'state': False, 'number': 0, 'msg': result.get('errmsg')}
            except ReadTimeout:
                return {'state': False, 'number': 0, 'msg': '网络连接超时'}
            except Exception:
                return {'state': False, 'number': 0, 'msg': "网络连接失败"}
        else:
            return {'state': False, 'number': 0, 'msg': 'None'}

class DingtalkReportList(models.Model):
    _name = 'dingtalk.report.list'
    _description = "日志列表"
    _rec_name = 'name'

    name = fields.Char(string='日志名')
    report_id = fields.Char(string='日志ID')
    remark = fields.Char(string='备注')
    dept_name = fields.Char(string='部门')
    # image1_url = fields.Char(string='图片1链接')
    # image2_url = fields.Char(string='图片2链接')
    creator_name = fields.Char(string='日志创建人')
    create_time = fields.Char(string='日志创时间')
    read_num = fields.Char(string='已读数')
    comment_num = fields.Char(string='评论数')
    comment_user_num = fields.Char(string='去重后评论数')
    like_num = fields.Char(string='点赞数')
    content_ids = fields.One2many(comodel_name='dingtalk.report.list.contents', inverse_name='report_id',
                               string=u'日志内容列表')
    receiver_user_ids = fields.One2many(comodel_name='dingtalk.report.list.receivers', inverse_name='report_id',
                               string=u'接受日志用户列表')
    follower_user_ids = fields.One2many(comodel_name='dingtalk.report.list.followers', inverse_name='report_id',
                               string=u'相关用户列表')
    image_url_ids = fields.One2many(comodel_name='dingtalk.report.list.images', inverse_name='report_id',
                               string=u'照片列表')
    template_id = fields.Many2one(comodel_name='dingtalk.report.template', string=u'日志模板', required=True)
    company_id = fields.Many2one(comodel_name='res.company',
                                 string=u'公司', default=lambda self: self.env.user.company_id.id)            
            

    @api.multi
    def update_report(self):
        """
        获取日志统计数据
        :param pid:
        :param pcode:
        :return:
        """
        self.get_report_statistics()
        self.get_report_receivers()
        
 
 
    @api.multi
    def get_report_statistics(self):
        """
        获取日志统计数据
        :param pid:
        :param pcode:
        :return:
        """
        
        url = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'get_report_statistics')]).value
        token = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'token')]).value
        # report_ids = self.env['dingtalk.report.list'].browse(self._context.get('active_ids',[]))
        data = {
            'report_id': self.report_id,
        }
        headers = {'Content-Type': 'application/json'}
        try:
            result = requests.post(url="{}{}".format(url, token), headers=headers, data=json.dumps(data), timeout=5)
            result = json.loads(result.text)
            logging.info(">>>获取日志统计数据返回结果{}".format(result))
            if result.get('errcode') == 0:
                res = result.get('result')
                data = {
                        'read_num': res.get('read_num'),
                        'comment_user_num': res.get('comment_user_num'),
                        'like_num': res.get('like_num'),
                        }
                report_list = self.env['dingtalk.report.list'].search(
                        [('report_id', '=', self.report_id)])
                if report_list:
                    report_list.write(data)
            else:
                raise UserError('获取日志统计数据失败，详情为:{}'.format(result.get('errmsg')))
        except ReadTimeout:
            raise UserError("网络连接超时！")
        logging.info(">>>获取日志统计数据结束...")  


    @api.multi
    def get_report_receivers(self):
        """
        获取日志接收人
        :param pid:
        :param pcode:
        :return:
        """
        
        url = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'get_report_receiver_list')]).value
        token = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'token')]).value
        # report_ids = self.env['dingtalk.report.list'].browse(self._context.get('active_ids',[]))

        data = {
            'report_id': self.report_id,
        }
        headers = {'Content-Type': 'application/json'}
        try:
            result = requests.post(url="{}{}".format(url, token), headers=headers, data=json.dumps(data), timeout=5)
            result = json.loads(result.text)
            logging.info(">>>获取日志统计数据返回结果{}".format(result))
            if result.get('errcode') == 0:
                res = result.get('result')
                userid_list = res.get('userid_list')
                if userid_list:
                    for userid in userid_list:
                        emp = self.env['hr.employee'].sudo().search([('din_id', '=', userid)])

                        data = {
                                'name': self.report_id,
                                'emp_id': emp.id,
                                'report_id': self.id,
                                }
                        report_receiver = self.env['dingtalk.report.list.receivers'].search(
                                [('report_id', '=', self.report_id), ('emp_id', '=', emp.id)])
                        if report_receiver:
                            pass
                        else:
                            report_receiver.create(data)
            else:
                raise UserError('获取日志统计数据失败，详情为:{}'.format(result.get('errmsg')))
        except ReadTimeout:
            raise UserError("网络连接超时！")
        logging.info(">>>获取日志统计数据结束...")  

class DownloadDingtalkList(models.TransientModel):
    _name = 'dingtalk.report.list.download'
    _description = "下载钉钉日志列表"
 
    date_from = fields.Datetime('开始日期')
    date_to = fields.Datetime('结束日期')


    @api.multi
    def get_report_list(self):
        """
        获取日志列表
        :param pid:
        :param pcode:
        :return:
        """

        url = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'get_report_list')]).value
        token = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'token')]).value
        templates = self.env['dingtalk.report.template'].browse(self._context.get('active_ids',[]))
        print('1111111111111111111111111111111111111',templates)
        for temp in templates:
            if temp:
                data = {
                    'start_time': int(time.mktime(self.date_from.timetuple())*1000),  #datetime转13位时间戳
                    'end_time': int(time.mktime(self.date_to.timetuple())*1000),
                    'template_name': temp.name,
                    'cursor': 0,
                    'size': 20,
                }
                headers = {'Content-Type': 'application/json'}
                try:
                    result = requests.post(url="{}{}".format(url, token), headers=headers, data=json.dumps(data), timeout=5)
                    result = json.loads(result.text)
                    logging.info(">>>获取日志列表返回结果{}".format(result))
                    if result.get('errcode') == 0:
                        d_res = result.get('result')
                        #获取日志列表
                        for report in d_res.get('data_list'):
                            data = {
                                'template_id': temp.id,
                                'name': report.get('creator_name') + "的" + report.get('template_name'),
                                'remark': report.get('remark'),
                                'dept_name': report.get('dept_name'),
                                'report_id': report.get('report_id'),
                                'creator_name': report.get('creator_name'),
                                'create_time': self.get_time_stamp(report.get('create_time')),
                            }
                            # if report.get('images'):
                            #     data.update({'image1_url': json.loads(report.get('images')[0]).get('image')})
                            #     if len(report.get('images')) >1:
                            #         data.update({'image2_url': json.loads(report.get('images')[1]).get('image')})
                            report_list = self.env['dingtalk.report.list'].search(
                                [('report_id', '=', report.get('report_id'))])
                            if report_list:
                                report_list.write(data)
                            else:
                                self.env['dingtalk.report.list'].create(data)
                            
                            
                            #获取日志内容
                            content = report['contents']
                            data = {
                            'report_id': report.get('report_id'),
                            'report_field_id': report_list.id,
                            'report_field_sort': content.get('sort'),
                            'report_field_type': content.get('type'),
                            'report_field_key': content.get('key'),
                            'report_field_value': content.get('value'),
                            }
                            report_content = self.env['dingtalk.report.list.contents'].search(
                                [('report_id', '=', report_list.id), ('report_field_sort', '=', content.get('sort'))])
                            if report_content:
                                report_content.write(data)
                            else:
                                self.env['dingtalk.report.list.contents'].create(data)

                    else:
                        raise UserError('获取日志列表失败，详情为:{}'.format(result.get('errmsg')))
                except ReadTimeout:
                    raise UserError("网络连接超时！")
        logging.info(">>>获取日志列表结束...")              




    @api.multi
    def get_report_list_byuser(self):
        """
        获取我的日志列表
        :param pid:
        :param pcode:
        :return:
        """
        
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if len(emp) > 1:
            return {'state': False, 'number': 0, 'msg': '登录用户关联了多个员工'}
        if emp and emp.din_id:
            url = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'get_report_list')]).value
            token = self.env['ali.dingtalk.system.conf'].search([('key', '=', 'token')]).value
            templates = self.env['dingtalk.report.template'].browse(self._context.get('active_ids',[]))
            for temp in templates:
                if temp:
                    data = {
                        'start_time': int(time.mktime(self.date_from.timetuple())*1000),  #datetime转13位时间戳
                        'end_time': int(time.mktime(self.date_to.timetuple())*1000),
                        'template_name': temp.name,
                        'userid': emp.din_id,
                        'cursor': 0,
                        'size': 20,
                    }
                    headers = {'Content-Type': 'application/json'}
                    try:
                        result = requests.post(url="{}{}".format(url, token), headers=headers, data=json.dumps(data), timeout=5)
                        result = json.loads(result.text)
                        logging.info(">>>获取日志列表返回结果{}".format(result))
                        if result.get('errcode') == 0:
                            d_res = result.get('result')
                            #获取日志列表
                            for report in d_res.get('data_list'):
                                data = {
                                    'template_id': temp.id,
                                    'name': report.get('template_name'),
                                    'remark': report.get('remark'),
                                    'dept_name': report.get('dept_name'),
                                    'report_id': report.get('report_id'),
                                    'creator_name': report.get('creator_name'),
                                    'create_time': self.get_time_stamp(report.get('create_time')),
                                }
                                if report.get('images'):
                                    data.update({'image1_url': json.loads(report.get('images')[0]).get('image')})
                                    if len(report.get('images')) >1:
                                        data.update({'image2_url': json.loads(report.get('images')[1]).get('image')})
                                report_list = self.env['dingtalk.report.list'].search(
                                    [('report_id', '=', report.get('report_id'))])
                                if report_list:
                                    report_list.write(data)
                                else:
                                    self.env['dingtalk.report.list'].create(data)
                                
                                #获取日志内容
                                report_list = self.env['dingtalk.report.list'].search(
                                    [('report_id', '=', report.get('report_id'))])
                                for content in report['contents']:
                                    data = {
                                    'name': report.get('template_name'),
                                    'report_field_id': report_list.id,
                                    'report_field_sort': content.get('sort'),
                                    'report_field_type': content.get('type'),
                                    'report_field_key': content.get('key'),
                                    'report_field_value': content.get('value'),
                                    }
                                    report_content = self.env['dingtalk.report.list.contents'].search(
                                        [('report_id', '=', report_list.id), ('report_sort', '=', content.get('sort'))])
                                    if report_content:
                                        report_content.write(data)
                                    else:
                                        self.env['dingtalk.report.list.contents'].create(data)

                        else:
                            raise UserError('获取我的日志列表失败，详情为:{}'.format(result.get('errmsg')))
                    except ReadTimeout:
                        raise UserError("网络连接超时！")
            logging.info(">>>获取我的日志列表结束...")              

    @api.model
    def get_time_stamp(self, timeNum):
        """
        将13位时间戳转换为时间
        :param timeNum:
        :return:
        """
        if timeNum:
            timestamp = float(timeNum / 1000)
            timearray = time.localtime(timestamp)
            otherstyletime = time.strftime("%Y-%m-%d %H:%M:%S", timearray)
            return otherstyletime

class DingtalkReportListContents(models.Model):
    _name = 'dingtalk.report.list.contents'
    _description = "日志内容"
    _rec_name = 'report_id'

    # name = fields.Char(string='日志名', required=True)
    report_field_sort = fields.Char(string='排序')
    report_field_type = fields.Char(string='类型')
    report_field_key = fields.Char(string='日志字段')
    report_field_value = fields.Char(string='填写内容')
    report_id = fields.Many2one(comodel_name='dingtalk.report.list', string='日志ID', required=True)


class DingtalkReportListReceivers(models.Model):
    _name = 'dingtalk.report.list.receivers'
    _description = "日志接收人员列表"
    _rec_name = 'report_id'

    # name = fields.Char(string='日志名', required=True)
    emp_id = fields.Many2one(comodel_name='hr.employee', string='接收人', required=True)
    report_id = fields.Many2one(comodel_name='dingtalk.report.list', string='日志ID', required=True)

class DingtalkReportListFollowers(models.Model):
    _name = 'dingtalk.report.list.followers'
    _description = "日志相关人员列表"
    _rec_name = 'report_id'

    # name = fields.Char(string='日志名', required=True)
    emp_id = fields.Many2one(comodel_name='hr.employee', string='关注者', required=True)
    report_id = fields.Many2one(comodel_name='dingtalk.report.list', string='日志ID', required=True)


class DingtalkReportListComments(models.Model):
    _name = 'dingtalk.report.list.comments'
    _description = "日志评论列表"
    _rec_name = 'report_id'

    # name = fields.Char(string='日志名', required=True)
    emp_id = fields.Many2one(comodel_name='hr.employee', string='评论人', required=True)
    report_comment = fields.Char(string='评论内容')
    report_id = fields.Many2one(comodel_name='dingtalk.report.list', string='日志ID', required=True)


class DingtalkReportListImages(models.Model):
    _name = 'dingtalk.report.list.images'
    _description = "日志相关图片"
    _rec_name = 'report_id'

    # name = fields.Char(string='日志名', required=True)
    image_url = fields.Char(string='图片链接')
    report_id = fields.Many2one(comodel_name='dingtalk.report.list', string='日志ID', required=True)

# class DingtalkReportListStatistics(models.Model):
#     _name = 'dingtalk.report.list.statistics'
#     _description = "日志统计数据"
#     _rec_name = 'name'

#     name = fields.Char(string='日志名', required=True)
#     read_num = fields.Char(string='已读数')
#     comment_num = fields.Char(string='评论数')
#     comment_user_num = fields.Char(string='去重后评论数')
#     like_num = fields.Char(string='点赞数')
#     report_id = fields.Many2one(comodel_name='dingtalk.report.list', string='日志ID', required=True)
