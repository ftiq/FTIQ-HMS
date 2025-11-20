# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class AcsConsentForm(models.Model):
    _inherit = "acs.hospitalization"

    consent_form_count = fields.Integer(string="Consent Form Count", compute="compute_consent_form_count", store=False)

    def compute_consent_form_count(self):
        for rec in self:
            rec.consent_form_count = self.env["acs.consent.form"].sudo().search_count([("hospitalization_id", "=", rec.id)])

    def action_open_consent_form(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("acs_consent_form.action_acs_consent_form")
        action["domain"] = [("hospitalization_id", "=", self.id)]
        action["context"] = {"default_hospitalization_id": self.id}
        return action

    def action_confirm(self):
        rec = super().action_confirm()
        for hospitalization in self:
            templates = self.env["acs.consent.form.template"].sudo().search([("acs_is_hospitalization_template", "=", True)])
            for template in templates:
                consent_vals = {
                    "subject": template.name,
                    "template_id": template.id,
                    "state": "draft",
                    "patient_id": hospitalization.patient_id.id,
                    "partner_id": hospitalization.patient_id.partner_id.id,
                    "physician_id": hospitalization.physician_id.id,
                    "company_id": hospitalization.company_id.id,
                    "date": fields.Datetime.now(),
                    "hospitalization_id": hospitalization.id,
                }
                consent = self.env["acs.consent.form"].sudo().create(consent_vals)
                consent.apply_template()
        return rec

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: