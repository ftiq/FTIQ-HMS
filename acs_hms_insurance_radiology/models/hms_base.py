# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class AcsRadiologyRequest(models.Model):
    _inherit = 'acs.radiology.request'

    insurance_id = fields.Many2one('hms.patient.insurance', string='Insurance Policy')
    claim_id = fields.Many2one('hms.insurance.claim', string='Claim')
    insurance_company_id = fields.Many2one('hms.insurance.company', related='insurance_id.insurance_company_id', string='Insurance Company', readonly=True, store=True)

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id and self.patient_id.insurance_ids:
            insurance_id = self.patient_id.insurance_ids[0]
            self.insurance_id = insurance_id.id
            self.pricelist_id = insurance_id.pricelist_id and insurance_id.pricelist_id.id or False
