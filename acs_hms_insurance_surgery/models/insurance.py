# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class InsuranceClaim(models.Model):
    _inherit = 'hms.insurance.claim'

    surgery_id = fields.Many2one('hms.surgery', string='Surgery')
    claim_for = fields.Selection(selection_add=[('surgery', 'Surgery')])
