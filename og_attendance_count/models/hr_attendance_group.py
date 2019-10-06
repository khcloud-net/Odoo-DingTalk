# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (C) 2019 OnGood
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
from requests import ReadTimeout
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrAttendanceGroup(models.Model):
    _name = 'hr.attendance.group'
    _rec_name = 'group_name'
    _description = '考勤组'

    ATTENDANCETYPE = [
        ('FIXED', '固定排班'),
        ('TURN', '轮班排班'),
        ('NONE', '无班次')
    ]

    group_name = fields.Char(string='考勤组名称', index=True)
    dept_name_list = fields.Many2many('hr.department', string=u'参与考勤部门')
    emp_ids = fields.Many2many('hr.employee', 'hr_attendance_group_and_employee_rel_01',
                               'group_id', 'emp_id', '成员列表')
    member_count = fields.Integer(string=u'成员人数')
    no_attendance_emp_ids = fields.Many2many('hr.employee', 'hr_attendance_group_and_employee_rel_02',
                                             'group_id', 'emp_id', '不参与考勤成员列表')
    attendance_type = fields.Selection(string=u'考勤类型', selection=ATTENDANCETYPE, default='NONE')
    manager_list = fields.Many2many('hr.employee', string=u'考勤组负责人', index=True)
    week_classes_list = fields.Char(string='班次时间展示')
    is_default = fields.Boolean(string=u'是否默认考勤组')
    default_class_id = fields.Many2one(comodel_name='hr.attendance.class', string=u'默认班次', index=True)
    is_active = fields.Boolean(string=u'是否启用')
    rule_id = fields.Many2one(string=u'加班规则', comodel_name='hr.attendance.rules')

    # 固定班制

    is_auto_holiday = fields.Boolean(string=u'节假日自动排休')
    # no_work_days = fields.One2many(comodel_name='hr.employee', inverse_name='attendance_group_id', string=u'必须打卡日期')
    # need_work_days = fields.One2many(comodel_name='hr.employee', inverse_name='attendance_group_id', string=u'不用打卡日期')
    class_list_ids = fields.One2many(comodel_name='hr.attendance.group.class.list',
                                     inverse_name='attendance_group_id', string=u'周班次列表', help="考勤组中的班次列表")

    # 排班制

    # class_run_days = fields.Char(string='排班周期')

    # 自由排班

    # 加班规则

    @api.onchange('dept_name_list')
    def onchange_dept_name_list(self):
        if self.dept_name_list:
            deps = self.get_dept_total(self.dept_name_list)
            emps = self.env['hr.employee'].search([('department_id', 'in', deps)])
            if len(emps) > 0:
                self.emp_ids = [(6, 0, emps.ids)]
                self.member_count = len(emps)
        else:
            self.emp_ids = False
            self.member_count = False

    @api.model
    def get_dept_total(self, dept_name_list):
        """
        获取部门下的子孙部门列表
        :param timeNum:
        :return:
        """
        dept_list = list()
        for dep in dept_name_list:
            dept_list.append(dep.id)
        i = 0
        while i <= 5:
            deps = self.env['hr.department'].sudo().search([('parent_id', 'in', dept_list)])
            for dep in deps:
                dept_list.append(dep.id)
            i += 1
        return dept_list

    @api.onchange('attendance_type')
    def onchange_attendance_type(self):
        """
        (0, 0,{ values })根据values里面的信息新建一个记录。
        (1,ID,{values}) 更新id=ID的记录（对id=ID的执行write 写入values里面的数据）
        (2,ID) 删除id=ID的数据（调用unlink方法，删除数据以及整个主从数据链接关系）
        """
        if self.attendance_type == 'FIXED':
            self.class_list_ids = [(2, self.id)]
            for w in ['1', '2', '3', '4', '5', '6']:
                data = {
                    'attendance_group_id': self.id,
                    'week_name': w,
                    'class_id': self.env['hr.attendance.class'].search([('is_default', '=', True)], limit=1).id,
                }

                self.class_list_ids = [(0, 0, data)]


class HrAttendanceGroupClassList(models.Model):
    _description = "考勤组内一周班次列表"
    _name = 'hr.attendance.group.class.list'
    _rec_name = 'week_name'

    WEEKDAY = [
        ('1', '周一'),
        ('2', '周二'),
        ('3', '周三'),
        ('4', '周四'),
        ('5', '周五'),
        ('6', '周六'),
        ('7', '周日')
    ]
    attendance_group_id = fields.Many2one(comodel_name='hr.attendance.group', string=u'考勤组', index=True)
    week_name = fields.Selection(string=u'星期', selection=WEEKDAY)
    class_id = fields.Many2one(comodel_name='hr.attendance.class', string=u'班次', index=True)


# class HrAttendanceGroupEmp(models.Model):
#     _description = "考勤组成员列表"
#     _name = 'hr.attendance.group.emp'
#     _rec_name = 'emp_id'

#     attendance_group_id = fields.Many2one(comodel_name='hr.attendance.group', string=u'考勤组', index=True)
#     emp_id = fields.Many2one(comodel_name='hr.employee', string=u'成员')


# class HrAttendanceGroupEmpNot(models.Model):
#     _description = "考勤组排除成员列表"
#     _name = 'hr.attendance.group.emp.not'
#     _rec_name = 'emp_id'

#     attendance_group_id = fields.Many2one(comodel_name='hr.attendance.group', string=u'考勤组', index=True)
#     emp_id = fields.Many2one(comodel_name='hr.employee', string=u'不参与考勤成员')