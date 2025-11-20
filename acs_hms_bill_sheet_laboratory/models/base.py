# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AcsLaboratoryRequest(models.Model):
    _inherit = 'acs.laboratory.request'
    
    bill_sheet_id = fields.Many2one('acs.bill.sheet', 'Bill Sheet')
