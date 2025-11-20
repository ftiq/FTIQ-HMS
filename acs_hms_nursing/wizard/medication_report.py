# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields
from datetime import time, date, datetime, timedelta


class AcsMedicationPlanning(models.TransientModel):
    _name = 'acs.medication.report.wiz'
    _description = "Medication Report"

    patient_id = fields.Many2one('hms.patient', string="Patient", required=True, readonly=True)
    hospitalization_id = fields.Many2one('acs.hospitalization', string="Hospitalization", required=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'acs.hospitalization' and self.env.context.get('active_id'):
            hospitalization = self.env['acs.hospitalization'].browse(self.env.context['active_id'])
            res['patient_id'] = hospitalization.patient_id.id
            res['hospitalization_id'] = hospitalization.id
        if self.env.context.get('active_model') == 'hms.patient' and self.env.context.get('active_id'):
            patient = self.env['hms.patient'].browse(self.env.context['active_id'])
            res['patient_id'] = patient.id
        return res

    def get_medications(self):
        domain = [('patient_id', '=', self.patient_id.id)]
        if self.start_date:
            domain.append(('date', '>=', self.start_date))
        if self.end_date:
            domain.append(('date', '<=', self.end_date))
        if self.hospitalization_id:
            domain.append(('hospitalization_id', '=', self.hospitalization_id.id))
        return self.env['acs.patient.medication'].search(domain).sorted('date')

    def action_print_report(self):
        return self.env.ref('acs_hms_nursing.acs_report_action_report_medication').report_action(self)