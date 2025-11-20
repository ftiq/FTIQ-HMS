# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PatientRadiologyTest(models.Model):
    _inherit = "patient.radiology.test"

    appointment_id = fields.Many2one('hms.appointment', string='Appointment', ondelete='restrict')
    treatment_id = fields.Many2one('hms.treatment', string='Treatment', ondelete='restrict')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: