# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api,fields,models,_


class AccountMove(models.Model):
    _inherit = 'account.move'

    emergency_id = fields.Many2one('acs.hms.emergency',  string='Emergency')
    hospital_invoice_type = fields.Selection(selection_add=[('emergency', 'Emergency')])
