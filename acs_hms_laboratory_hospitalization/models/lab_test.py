# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PatientLabTest(models.Model):
    _inherit = "patient.laboratory.test"

    hospitalization_id = fields.Many2one('acs.hospitalization', string='Hospitalization', ondelete='restrict')
    print_in_discharge = fields.Boolean("Print in Discharge Report")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: