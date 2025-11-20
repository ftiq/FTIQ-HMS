# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"
    
    def acs_get_nurse_round_data(self, invoice_id=False):
        for ward_round_line in self.hospitalization_id.ward_round_ids.filtered(lambda w: w.invoice_id):
            ward_round_line.invoice_id = False