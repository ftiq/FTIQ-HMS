# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    insurance_id = fields.Many2one('hms.patient.insurance', string='Insurance Policy')
    claim_id = fields.Many2one('hms.insurance.claim', 'Claim')
    insurance_company_id = fields.Many2one('hms.insurance.company', related='claim_id.insurance_company_id', string='Insurance Company', readonly=True)
    claim_sheet_id = fields.Many2one('acs.claim.sheet', string='Claim Sheet')
    patient_invoice_id = fields.Many2one('account.move', string='Patient Invoice')
    patient_invoice_amount = fields.Monetary(related="patient_invoice_id.amount_total", string='Patient Invoice Amount', store=True)
    insurance_invoice_id = fields.Many2one('account.move', string='Insurance Invoice')
    insurance_invoice_amount = fields.Monetary(related="insurance_invoice_id.amount_total", string='Insurance Invoice Amount', store=True)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    claim_id = fields.Many2one('hms.insurance.claim', 'Claim')
    insurance_company_id = fields.Many2one('hms.insurance.company', related='claim_id.insurance_company_id', string='Insurance Company', readonly=True)

