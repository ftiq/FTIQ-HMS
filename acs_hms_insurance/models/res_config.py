# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _

class ResCompany(models.Model):
    _inherit = "res.company"

    acs_insurance_claim_sign = fields.Boolean('Signature in Insurance Claims', help='Set this True if need patient and doctor sign on Claims.')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    acs_insurance_claim_sign = fields.Boolean('Signature in Insurance Claims', related='company_id.acs_insurance_claim_sign', readonly=False, help='Set this True if need patient and doctor sign on Claims.')