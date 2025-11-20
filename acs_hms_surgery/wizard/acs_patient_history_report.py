# coding: utf-8
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import models

class AcsPatientHistoryReportWiz(models.TransientModel):
    _inherit = 'acs.patient.history.report.wiz'

    def acs_patient_history_report(self):
        data = super().acs_patient_history_report()
        surgeries = self.env['hms.surgery'].search([('patient_id', '=', self.patient_id.id),('start_date', '>=', self.acs_date_from),('start_date', '<=', self.acs_date_to)])
        if surgeries:
            data['surgeries'] = surgeries
        return data