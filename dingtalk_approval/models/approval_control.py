# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DingTalkApprovalControl(models.Model):
    _name = 'dingtalk.approval.control'
    _description = "审批单据关联"
    _rec_name = 'oa_model_id'

    oa_model_id = fields.Many2one(comodel_name='ir.model', string=u'OA协同单据', required=True)
    template_id = fields.Many2one(comodel_name='dingtalk.approval.template', string=u'审批模板', required=True)
    company_id = fields.Many2one(comodel_name='res.company',
                                 string=u'公司', default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [
        ('oa_model_id_uniq', 'unique(oa_model_id)', u'已存在OA协同单据对应的审批模板!'),
    ]

    @api.model
    def get_oa_model(self):
        oa_models = self.env['dingtalk.approval.control'].sudo().search([])
        model_list = list()
        for oa_model in oa_models:
            model_list.append(oa_model.oa_model_id.model)
        return model_list
