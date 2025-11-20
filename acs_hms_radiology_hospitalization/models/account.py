# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"
    
    def acs_get_radiology_data(self, invoice_id=False):
        for radiology_request in self.hospitalization_id.radiology_request_ids.filtered(lambda radio_req: radio_req.invoice_id):
            radiology_request.state = 'to_invoice'
            radiology_request.invoice_id = False