# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    patient_registartion_sms_template_id = fields.Many2one("sms.template", "Patient Registration SMS")
    appointment_registartion_sms_template_id = fields.Many2one("sms.template", "Appointment Registration SMS")
    acs_reminder_sms_template_id = fields.Many2one("sms.template", "Appointment Reminder SMS")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: