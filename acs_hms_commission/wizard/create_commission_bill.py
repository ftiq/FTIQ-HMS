# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class ACSCommissionBill(models.TransientModel):
    _inherit = "commission.bill"

    def create_bill(self, line):
        res = super(ACSCommissionBill, self).create_bill(line)
        res.hospital_invoice_type = 'commission'
        return res
