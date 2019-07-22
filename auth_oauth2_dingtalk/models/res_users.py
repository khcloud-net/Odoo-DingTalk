# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, AccessDenied
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def auth_oauth_dingtalk(self, provide_id, oauth_uid):
        if provide_id == 'dingtalk':
            user_ids = self.search([('oauth_uid', '=', oauth_uid)])
        else:
            user_ids = self.search([('oauth_provider_id', '=', provide_id), ('oauth_uid', '=', oauth_uid)])
        _logger.info("user: %s", user_ids)
        if not user_ids or len(user_ids) > 1:
            return AccessDenied
        return (self.env.cr.dbname, user_ids[0].login, oauth_uid)

    @api.model
    def _check_credentials(self, password):
        try:
            return super(ResUsers, self)._check_credentials(password)
        except AccessDenied:
            res = self.sudo().search([('id', '=', self.env.uid), ('oauth_uid', '=', password)])
            if not res:
                raise
