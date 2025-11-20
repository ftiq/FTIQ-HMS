# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    patient_hb_measure_uom = fields.Char(string='Patient Hemoglobin unit of measure', config_parameter='acs_hms_gynec.acs_patient_hb_uom')
    patient_urine_measure_uom = fields.Char(string='Patient Urine unit of measure', config_parameter='acs_hms_gynec.acs_patient_urine_uom')
    patient_screatinine_measure_uom = fields.Char(string='Patient S Creatinine unit of measure', config_parameter='acs_hms_gynec.acs_patient_screatinine_uom')