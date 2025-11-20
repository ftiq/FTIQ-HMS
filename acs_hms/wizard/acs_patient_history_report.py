# coding: utf-8
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
from odoo.exceptions import UserError
from datetime import timedelta

class AcsPatientHistoryReportWiz(models.TransientModel):
    _name = 'acs.patient.history.report.wiz'
    _description = "Patient History Report"

    acs_date_from = fields.Date(string='Date From', required=True)
    acs_date_to = fields.Date(string="Date To", required=True)
    patient_id=fields.Many2one('hms.patient',string="Patient",readonly=True)

    def default_get(self,fields):
        res = super().default_get(fields)
        res["patient_id"] = self.env.context.get("active_id")
        return res

    def acs_patient_history_report(self):
        patient = self.patient_id
        appointments = self.env['hms.appointment'].search([('patient_id', '=', patient.id),('date', '>=', self.acs_date_from),('date', '<', self.acs_date_to+ timedelta(days=1))])
        data = {
            'patient_ids': [patient.id],
            'patient_name': patient.name,
            'date_from': self.acs_date_from.strftime('%Y-%m-%d'),
            'date_to': self.acs_date_to.strftime('%Y-%m-%d'),
            'appointments': appointments,
        }
        return data

    def acs_print_patient_history_report(self):
        if self.acs_date_from > self.acs_date_to:
            raise UserError('Select Correct Date Range')
        return self.env.ref('acs_hms.acs_action_report_patient_history').report_action(self)