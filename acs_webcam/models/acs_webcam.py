# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def acs_webcam_update_image(self, res_id, image_field=None, image_data=None):
        if not res_id or not image_field or not image_data:
            return False
        partner = self.env['res.partner'].sudo().search([('id', '=', res_id)], limit=1)
        _logger.info("\n\n Is this Partner ----- %s", partner)
        if partner:
            image_fd = image_field or "image_1920"
            partner.write({image_fd: image_data})
            return True
        return False

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def acs_webcam_update_image(self, res_id, image_field=None, image_data=None):
        if not res_id or not image_field or not image_data:
            return False
        user = self.env['res.users'].sudo().search([('id', '=', res_id)], limit=1)
        _logger.info("\n\n Is this User ----- %s", user)
        if user:
            image_fd = image_field or "image_1920"
            user.write({image_fd: image_data})
            return True
        return False