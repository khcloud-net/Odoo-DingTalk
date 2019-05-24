odoo.define('dingtalk.user.callback.button', function (require) {
    "use strict";

    let ListController = require('web.ListController');
    let Dialog = require('web.Dialog');
    let core = require('web.core');
    let QWeb = core.qweb;
    let rpc = require('web.rpc');

    let save_data = function () {
        rpc.query({
            model: 'dingtalk.users.callback',
            method: 'get_all_call_back',
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

    ListController.include({
        renderButtons: function ($node) {
            let $buttons = this._super.apply(this, arguments);
            let tree_model = this.modelName;
            if (tree_model == 'dingtalk.users.callback') {
                let but = "<button type=\"button\" t-if=\"widget.modelName == 'dingtalk.users.callback'\" class=\"btn btn-primary\">获取回调列表</button>";
                let button2 = $(but).click(this.proxy('pull_dingtalk_user_callback'));
                this.$buttons.append(button2);
            }
            return $buttons;
        },
        pull_dingtalk_user_callback: function () {
            new Dialog(this, {
                title: "拉取回调列表",
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
                $content: $(QWeb.render('PullDingTalkUserCallback', {widget: this, data: []}))
            }).open();
        },
    });
});
