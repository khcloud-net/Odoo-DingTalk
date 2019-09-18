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
import logging
from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrAttendancePlan(models.Model):
    _name = "hr.attendance.plan"
    _rec_name = 'plan_id'
    _description = "排班列表"

    emp_id = fields.Many2one(comodel_name='hr.employee', string=u'员工')
    group_id = fields.Many2one(comodel_name='hr.attendance.group', string=u'考勤组')
    class_id = fields.Char(string='班次')
    check_type = fields.Selection(string=u'打卡类型', selection=[('OnDuty', '上班打卡'), ('OffDuty', '下班打卡')])
    approve_id = fields.Char(string='审批id', help="没有的话表示没有审批单")
    class_setting_id = fields.Char(string='班次配置id', help="没有的话表示使用全局班次配置")
    plan_check_time = fields.Datetime(string=u'打卡时间', help="数据库中存储为不含时区的时间UTC=0")


class HrAttendancePlanTran(models.TransientModel):
    _name = "hr.attendance.plan.tran"
    _description = "排班列表查询"

    start_date = fields.Date(string=u'开始日期', required=True)
    stop_date = fields.Date(string=u'结束日期', required=True, default=str(fields.datetime.now()))

    @api.multi
    def get_plan_lists(self):
        """
        获取企业考勤排班详情
        :return:
        """
        self.ensure_one()
        self.start_pull_plan_lists(self.start_date, self.stop_date)
        action = self.env.ref('og_attendance_count.hr_attendance_plan_action')
        action_dict = action.read()[0]
        return action_dict

    @api.model
    def start_pull_plan_lists(self, start_date, stop_date):
        """
        拉取排班信息
        :param start_date: string 查询的开始日期
        :param stop_date: string 查询的结束日期
        :return:
        """

        # 删除已存在的排班信息
        self.env['hr.attendance.plan'].sudo().search([
            ('plan_check_time', '>=', start_date), ('plan_check_time', '<=', stop_date)]).unlink()

        din_client = self.env['attendance.api.tools'].get_client()
        logging.info(">>>------开始获取排班信息-----------")
        work_date = start_date
        while work_date <= stop_date:
            offset = 0
            size = 200
            while True:
                result = din_client.attendance.listschedule(work_date, offset=offset, size=size)
                # logging.info(">>>获取排班信息返回结果%s", result)
                if result.get('ding_open_errcode') == 0:
                    res_result = result.get('result')
                    plan_data_list = list()
                    for schedules in res_result['schedules']['at_schedule_for_top_vo']:
                        plan_data = {
                            'class_setting_id': schedules['class_setting_id'] if 'class_setting_id' in schedules else "",
                            'check_type': schedules['check_type'] if 'check_type' in schedules else "",
                            'plan_id': schedules['plan_id'] if 'plan_id' in schedules else "",
                            'class_id': schedules['class_id'] if 'class_id' in schedules else "",
                        }
                        if 'plan_check_time' in schedules:
                            utc_plan_check_time = datetime.strptime(
                                schedules['plan_check_time'], "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)
                            plan_data.update({'plan_check_time': utc_plan_check_time})
                        simple = self.env['hr.attendance.group'].search(
                            [('group_id', '=', schedules['group_id'])], limit=1)
                        employee = self.env['hr.employee'].search([('ding_id', '=', schedules['userid'])], limit=1)
                        plan_data.update({
                            'group_id': simple.id if simple else False,
                            'user_id': employee.id if employee else False,
                        })
                        plan_data_list.append(plan_data)
                    self.env['hr.attendance.plan'].create(plan_data_list)
                    # plan = self.env['hr.attendance.plan'].search([('plan_id', '=', schedules['plan_id'])])
                    # if not plan:
                    #     self.env['hr.attendance.plan'].create(plan_data)
                    # else:
                    #     plan.write(plan_data)
                    if not res_result['has_more']:
                        break
                    else:
                        offset += size
                else:
                    raise UserError("获取企业考勤排班详情失败: {}".format(result['errmsg']))
            work_date = work_date + timedelta(days=1)
        logging.info(">>>------结束获取排班信息-----------")
        return True

    @api.multi
    def clear_hr_attendance_plan(self):
        """
        清除已下载的所有钉钉排班记录（仅用于测试，生产环境将删除该函数）
        """
        self._cr.execute("""
            delete from hr_attendance_plan
        """)
