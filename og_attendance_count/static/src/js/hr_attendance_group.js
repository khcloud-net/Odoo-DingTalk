/**
 *    Copyright (C) 2019 OnGood
 *
 *    This program is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU Affero General Public License as
 *    published by the Free Software Foundation, either version 3 of the
 *    License, or (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU Affero General Public License for more details.
 *
 *    You should have received a copy of the GNU Affero General Public License
 *    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 **/

odoo.define('hr.attendance.group.button', function (require) {
    "use strict";

    let ListController = require('web.ListController');
    let Dialog = require('web.Dialog');
    let core = require('web.core');
    let QWeb = core.qweb;
    let rpc = require('web.rpc');

    let save_data = function () {
        this.do_notify("请稍后...", "正在查询！!");
        getSimpleGroups();
    };

    let get_sim_emps_data = function () {
        let def = rpc.query({
            model: 'hr.attendance.group',
            method: 'get_sim_emps',
            args: [],
        }).then(function (result) {
            if (result.state) {
                location.reload();
            } else {
                new Dialog.confirm(this, result.msg, {
                    'title': '结果提示',
                });
            }
        });
    };

    let getSimpleGroups = function () {
        let def = rpc.query({
            model: 'hr.attendance.group',
            method: 'get_simple_groups',
            args: [],
        }).then(function (result) {
            if (result) {
                location.reload();
            }
        });
    };

    ListController.include({
        renderButtons: function ($node) {
            let $buttons = this._super.apply(this, arguments);
            let tree_model = this.modelName;
            if (tree_model == 'hr.attendance.group') {
                let but = "<button type=\"button\" t-if=\"widget.modelName == 'hr.attendance.group'\" class=\"btn btn-primary o_pull_hr.attendance.group\" groups=\"attendance_base.manage_groups\">拉取钉钉考勤组</button>";
                let button2 = $(but).click(this.proxy('open_simple_action'));
                this.$buttons.append(button2);
                let but3 = "<button type=\"button\" t-if=\"widget.modelName == 'hr.attendance.group'\" class=\"btn btn-secondary\" groups=\"attendance_base.manage_groups\">获取钉钉考勤组成员</button>";
                let button3 = $(but3).click(this.proxy('get_simple_emps_action'));
                this.$buttons.append(button3);
            }
            return $buttons;
        },
        open_simple_action: function () {
            new Dialog(this, {
                title: "拉取考勤",
                size: 'medium',
                buttons: [
                    {
                        text: "确定",
                        classes: 'btn-primary',
                        close: true,
                        click: save_data
                    }, {
                        text: "取消",
                        close: true
                    }
                ],
                $content: $(QWeb.render('PullDinDinSimpleGroups', {widget: this, data: []}))
            }).open();
        },
        get_simple_emps_action: function () {
            new Dialog(this, {
                title: "获取考勤组成员",
                size: 'medium',
                buttons: [
                    {
                        text: "确定",
                        classes: 'btn-primary',
                        close: true,
                        click: get_sim_emps_data
                    }, {
                        text: "取消",
                        close: true
                    }
                ],
                $content: $(QWeb.render('GetDinDinSimpleGroupsEmps', {widget: this, data: []}))
            }).open();
        },


    });
});
