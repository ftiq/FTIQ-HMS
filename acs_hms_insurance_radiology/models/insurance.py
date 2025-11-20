# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class InsuranceClaim(models.Model):
    _inherit = 'hms.insurance.claim'

    radiology_request_id = fields.Many2one('acs.radiology.request', string='Radiology Request')
    claim_for = fields.Selection(selection_add=[('radiology', 'Radiology')])
