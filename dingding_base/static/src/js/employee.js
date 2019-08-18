/**
 *    Copyright (C) 2019 SuXueFeng
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

odoo.define('dingding_base.res.employee.synchronous.button', function (require) {
    "use strict";

    let KanbanController = require('web.KanbanController');
    let ListController = require('web.ListController');
    let Dialog = require('web.Dialog');
    let core = require('web.core');
    let QWeb = core.qweb;
    let rpc = require('web.rpc');

    let start_synchronous_employee = function () {
        rpc.query({
            model: 'hr.employee',
            method: 'synchronous_dingding_employee',
            args: [],
        }).then(function (result) {
            if(result.state){
                location.reload();
            }else{
                alert(result.msg);
            }
        });
    };

    ListController.include({
        renderButtons: function ($node) {
            let $buttons = this._super.apply(this, arguments);
            let tree_model = this.modelName;
            if (tree_model == 'hr.employee') {
                let but = "<button type=\"button\" t-if=\"widget.modelName == 'hr.employee'\" class=\"btn btn-primary\">同步钉钉员工</button>";
                let button2 = $(but).click(this.proxy('synchronous_dingding_employee_list'));
                this.$buttons.append(button2);
            }
            return $buttons;
        },
        synchronous_dingding_employee_list: function () {
            new Dialog(this, {
                title: "同步钉钉员工",
                size: 'medium',
                buttons: [
                    {
                        text: "开始同步",
                        classes: 'btn-primary',
                        close: true,
                        click: start_synchronous_employee
                    }, {
                        text: "取消同步",
                        close: true
                    }
                ],
                $content: $(QWeb.render('SynchronousDingEmployeeTemplate', {widget: this, data: []}))
            }).open();
        },
    });

    KanbanController.include({
        renderButtons: function ($node) {
            let $buttons = this._super.apply(this, arguments);
            let tree_model = this.modelName;
            if (tree_model == 'hr.employee') {
                let but = "<button type=\"button\" t-if=\"widget.modelName == 'hr.employee'\" class=\"btn btn-primary\">同步钉钉员工</button>";
                let button2 = $(but).click(this.proxy('synchronous_dingding_employee_kanban'));
                this.$buttons.append(button2);
            }
            return $buttons;
        },
        synchronous_dingding_employee_kanban: function () {
            new Dialog(this, {
                title: "同步钉钉员工",
                size: 'medium',
                buttons: [
                    {
                        text: "开始同步",
                        classes: 'btn-primary',
                        close: true,
                        click: start_synchronous_employee
                    }, {
                        text: "取消同步",
                        close: true
                    }
                ],
                $content: $(QWeb.render('SynchronousDingEmployeeTemplate', {widget: this, data: []}))
            }).open();
        },
    });

});
