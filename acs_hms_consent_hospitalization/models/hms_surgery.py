# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class SurgeryConsent(models.Model):
    _inherit = "hms.surgery"

    consent_form_count = fields.Integer(string="Consent Form Count", compute="_compute_consent_form_count", store=False)

    def _compute_consent_form_count(self):
        for rec in self:
            rec.consent_form_count = self.env["acs.consent.form"].sudo().search_count([("surgery_id", "=", rec.id)])

    def action_open_consent_form(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("acs_consent_form.action_acs_consent_form")
        action["domain"] = [("surgery_id", "=", self.id)]
        action["context"] = {"default_surgery_id": self.id}
        return action

    def action_confirm(self):
        rec = super().action_confirm()
        for surgery in self:
            templates = self.env["acs.consent.form.template"].sudo().search([("acs_is_surgery_template", "=", True)])
            for template in templates:
                consent_vals = {
                    "subject": template.name,
                    "template_id": template.id,
                    "state": "draft",
                    "patient_id": surgery.patient_id.id,
                    "partner_id": surgery.patient_id.partner_id.id,
                    "date": fields.Datetime.now(),
                    "surgery_id": surgery.id,
                    "physician_id": surgery.primary_physician_id.id,
                }
                consent = self.env["acs.consent.form"].sudo().create(consent_vals) 
                consent.apply_template()    
        return rec

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: