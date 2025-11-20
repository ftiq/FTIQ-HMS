# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AcsInsurancePreApproval(models.Model):
    _inherit = 'acs.insurance.pre.approval'
    _description = 'Insurance Pre-Approval Request'
    
    acs_surgery_id = fields.Many2one('hms.surgery', string='If surgical, name of surgery')
