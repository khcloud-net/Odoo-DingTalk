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

odoo.define('hr.attendance.info.button', function (require) {
    "use strict";

    let ListController = require('web.ListController');

    ListController.include({
        renderButtons: function ($node) {
            let $buttons = this._super.apply(this, arguments);
            let tree_model = this.modelName;
            if (tree_model == 'hr.attendance.info') {
                let but = "<button type=\"button\" t-if=\"widget.modelName == 'hr.attendance.info'\" class=\"btn btn-secondary\" groups=\"og_attendance_count.manage_groups\">计算考勤结果</button>";
                let button2 = $(but).click(this.proxy('open_attendance_info_list_action'));
                this.$buttons.append(button2);
            }
            return $buttons;
        },
        open_attendance_info_list_action: function () {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'hr.attendance.info.tran',
                target: 'new',
                views: [[false, 'form']],
                context: [],
            });
        },
    });
});
