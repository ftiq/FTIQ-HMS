# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
# Part of AlmightyCS See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    acs_auto_close_referral_days = fields.Integer(
        related='company_id.acs_auto_close_referral_days',
        string='Auto Close Referral Days',
        readonly=False,
        help='Number of days after which a referral will be automatically closed.'
    )
    acs_auto_patient_creation = fields.Boolean(
        related='company_id.acs_auto_patient_creation', string='Auto Create Patient', readonly=False,
        help='Automatically create a patient record when a referral is created from portal.'
    )


class ResCompany(models.Model):
    _inherit = "res.company"

    acs_auto_close_referral_days = fields.Integer(string='Auto Close Referral Days', default=10)
    acs_auto_patient_creation = fields.Boolean(string='Auto Create Patient', default=False)