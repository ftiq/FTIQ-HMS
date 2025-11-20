# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, tools


class AcsConsentForm(models.Model):
    _inherit = 'acs.consent.form'

    patient_id = fields.Many2one('hms.patient', string='Patient', ondelete="restrict", 
        help="Patient whose consent form to be attached", tracking=True)
    physician_id = fields.Many2one('hms.physician',string='Doctor', ondelete="restrict", 
        help="Doctor who provided consent form to the patient", tracking=True)
    appointment_id = fields.Many2one('hms.appointment', string='Appointment', ondelete="restrict", 
        help="Patient Appointment")

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.partner_id = self.patient_id.partner_id

    @api.onchange('physician_id')
    def onchange_physician_id(self):
        if self.physician_id:
            self.user_id = self.physician_id.user_id


class ACSPatient(models.Model):
    _inherit = 'hms.patient' 

    def action_open_consent_form(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_consent_form.action_acs_consent_form")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action


class HmsAppointment(models.Model):
    _inherit = 'hms.appointment' 

    def _consent_form_count(self):
        for rec in self:
            rec.consent_form_count = len(rec.sudo().consent_form_ids)

    consent_form_ids = fields.One2many('acs.consent.form', 'appointment_id', string='Consent Form', groups="acs_consent_form.group_consent_form_manager")
    consent_form_count = fields.Integer(compute='_consent_form_count', string='# Consent Form')

    def action_open_consent_form(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_consent_form.action_acs_consent_form")
        action['domain'] = [('appointment_id','=',self.id)]
        action['context'] = {
            'default_appointment_id': self.id,
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_physician_id': self.physician_id and self.physician_id.id or False,
        }
        return action

    def appointment_confirm(self):
        rec = super().appointment_confirm()
        for appointment in self:
            templates = self.env["acs.consent.form.template"].sudo().search([("acs_is_appointment_template", "=", True)])
            for template in templates:
                consent_vals = {
                    "subject": template.name,
                    "template_id": template.id,
                    "state": "draft",
                    "patient_id": appointment.patient_id.id,
                    "partner_id": appointment.patient_id.partner_id.id,
                    "physician_id": appointment.physician_id.id,
                    "date": fields.Datetime.now(),
                    "appointment_id": appointment.id,
                }
                consent = self.env["acs.consent.form"].sudo().create(consent_vals)
                consent.apply_template()
        return rec


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            record.acs_create_sequence(name='Consent Form', code='acs.consent.form', prefix='CF')
        return res


class AcsConsentFormTemplate(models.Model):
    _inherit = 'acs.consent.form.template'

    acs_is_appointment_template = fields.Boolean("Appointment Template", default=False)
   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: