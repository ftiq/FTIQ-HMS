# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    acs_patient_reg_template_id = fields.Many2one('acs.whatsapp.template', 'Patient Registration Template')
    acs_appointment_confirmation_template_id = fields.Many2one('acs.whatsapp.template', 'Appointment Registration Template')
    acs_appointment_reminder_template_id = fields.Many2one('acs.whatsapp.template', 'Appointment Reminder Template')
    acs_appointment_reschedule_template_id = fields.Many2one('acs.whatsapp.template', 'Appointment Reschedule Template')
    acs_whatsapp_birthday_template_id = fields.Many2one('acs.whatsapp.template',string="Birthday WhatsApp Template")
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: