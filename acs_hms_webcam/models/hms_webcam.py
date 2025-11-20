# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class HmsPatient(models.Model):
    _inherit = 'hms.patient'

    @api.model
    def acs_webcam_update_image(self, res_id, image_field=None, image_data=None):
        if not res_id or not image_field or not image_data:
            return False
        patient = self.env['hms.patient'].sudo().search([('id', '=', res_id)], limit=1)
        _logger.info("\n\n Is this Patient ----- %s", patient)
        if patient:
            image_fd = image_field or "image_1920"
            patient.write({image_fd: image_data})
            return True
        return False
    
class HmsPhysician(models.Model):
    _inherit = 'hms.physician'

    @api.model
    def acs_webcam_update_image(self, res_id, image_field=None, image_data=None):
        if not res_id or not image_field or not image_data:
            return False
        physician = self.env['hms.physician'].sudo().search([('id', '=', res_id)], limit=1)
        _logger.info("\n\n Is this Physician ----- %s", physician)
        if physician:
            image_fd = image_field or "image_1920"
            physician.write({image_fd: image_data})
            return True
        return False