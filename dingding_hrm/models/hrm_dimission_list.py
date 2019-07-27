# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _
from odoo.addons.ali_dindin.dingtalk.main import (client, list_cut,
                                                  stamp_to_time)
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DingDingHrmDimissionList(models.Model):
    _name = 'dingding.hrm.dimission.list'
    _description = "离职员工信息"
    _rec_name = 'emp_id'

    REASONTYPE = [
        ('1', '家庭原因'),
        ('2', '个人原因'),
        ('3', '发展原因'),
        ('4', '合同到期不续签'),
        ('5', '协议解除'),
        ('6', '无法胜任工作'),
        ('7', '经济性裁员'),
        ('8', '严重违法违纪'),
        ('9', '其他'),
    ]
    PRESTATUS = [
        ('1', '待入职'),
        ('2', '试用期'),
        ('3', '正式'),
        ('4', '未知'),
        ('5', '未知'),
    ]
    emp_id = fields.Many2one(comodel_name='hr.employee',
                             string='员工')
    din_id = fields.Char(string='钉钉id')
    last_work_day = fields.Datetime(string='最后工作时间')
    department_ids = fields.Many2many(comodel_name='hr.department', relation='hrm_dimission_and_depatment_rel',
                                      column1='list_id', column2='dept_id', string='部门')
    reason_memo = fields.Text(string="离职原因")
    reason_type = fields.Selection(string='离职类型', selection=REASONTYPE)
    pre_status = fields.Selection(string='离职前工作状态', selection=PRESTATUS)
    handover_userid = fields.Many2one(
        comodel_name='hr.employee', string='离职交接人')
    status = fields.Selection(string='离职状态', selection=[
                              ('1', '待离职'), ('2', '已离职')])
    main_dept_name = fields.Many2one(
        comodel_name='hr.department', string='离职前主部门')
    company_id = fields.Many2one(
        comodel_name='res.company', string='公司', default=lambda self: self.env.user.company_id.id)


class GetDingDingHrmDimissionList(models.TransientModel):
    _name = 'dingding.get.hrm.dimission.list'
    _description = '获取离职员工信息'

    emp_ids = fields.Many2many(comodel_name='hr.employee', relation='dingding_hrm_dimission_list_and_hr_employee_rel',
                               column1='list_id', column2='emp_id', string='员工', required=True)
    is_all_emp = fields.Boolean(string='全部离职员工')

    @api.onchange('is_all_emp')
    def onchange_all_emp(self):
        if self.is_all_emp:
            emps = self.env['hr.employee'].search(
                [('din_id', '!=', ''), ('work_status', '=', '3')])
            self.emp_ids = [(6, 0, emps.ids)]
        else:
            self.emp_ids = False

    
    def get_hrm_dimission_list(self):
        """
        批量获取员工离职信息
        """
        logging.info(">>>获取钉钉获取离职员工信息start")
        din_ids = list()
        for user in self.emp_ids:
            din_ids.append(user.din_id)
        user_list = list_cut(din_ids, 50)
        for u in user_list:
            self.dimission_list(u)
        logging.info(">>>获取钉钉获取离职员工信息end")
        action = self.env.ref(
            'dingding_hrm.dingding_hrm_dimission_list_action')
        action_dict = action.read()[0]
        return action_dict

    @api.model
    def dimission_list(self, user_ids):
        """
        批量获取员工离职信息
        根据传入的staffId列表，批量查询员工的离职信息
        :param userid_list: 员工id
        """
        logging.info(">>>获取钉钉获取离职员工信息start")
        if len(user_ids) > 50:
            raise UserError(_("钉钉仅支持批量查询小于等于50个员工!"))
        try:
            result = client.employeerm.listdimission(userid_list=user_ids)
            logging.info(">>>批量获取员工离职信息返回结果%s", result)

            # if len(result) < 1:
            #     raise UserError(_("选择的员工未离职!"))
            if result.get('emp_dimission_info_vo'):
                for res in result.get('emp_dimission_info_vo'):
                    if res.get('main_dept_id'):
                        main_dept = self.env['hr.department'].search(
                            [('din_id', '=', res.get('main_dept_id'))])
                    dept_list = list()
                    if res.get('dept_list'):
                        for depti in res['dept_list']['emp_dept_v_o']:
                            hr_dept = self.env['hr.department'].search(
                                [('din_id', '=', depti.get('dept_id'))])
                            if hr_dept:
                                dept_list.append(hr_dept.id)
                    data = {
                        'din_id': res.get('userid'),
                        'last_work_day': stamp_to_time(res.get('last_work_day')),
                        'department_ids': [(6, 0, dept_list)] if dept_list else '',
                        'reason_memo': res.get('reason_memo'),
                        'reason_type': str(res.get('reason_type')) if res.get('reason_type') else '9',
                        'pre_status': str(res.get('pre_status')),
                        'status': str(res.get('status')),
                        'main_dept_name': main_dept.id if main_dept else False,
                    }
                    if res.get('handover_userid'):
                        handover_userid = self.env['hr.employee'].search(
                            [('din_id', '=', res.get('handover_userid'))])
                        data.update({'handover_userid': handover_userid.id})
                    emp = self.env['hr.employee'].search(
                        [('din_id', '=', res.get('userid'))])
                    if emp:
                        data.update({'emp_id': emp[0].id})
                    hrm = self.env['dingding.hrm.dimission.list'].search(
                        [('din_id', '=', res.get('userid'))])
                    if hrm:
                        hrm.write(data)
                    else:
                        self.env['dingding.hrm.dimission.list'].create(data)

        except Exception as e:
            raise UserError(e)
        logging.info(">>>获取获取离职员工信息end")
