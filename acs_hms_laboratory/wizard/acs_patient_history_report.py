# coding: utf-8
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import models

class AcsPatientHistoryReportWiz(models.TransientModel):
    _inherit = 'acs.patient.history.report.wiz'

    def acs_patient_history_report(self):
        data = super().acs_patient_history_report()
        laboratory = self.env['acs.laboratory.request'].search([('patient_id', '=', self.patient_id.id),('date', '>=', self.acs_date_from),('date', '<=', self.acs_date_to)])
        if laboratory:
            data['laboratory'] = laboratory
        return data