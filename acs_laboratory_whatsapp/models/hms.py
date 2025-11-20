# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AcsLaboratoryRequest(models.Model):
    _name = 'acs.laboratory.request'
    _inherit = ['acs.laboratory.request','acs.whatsapp.mixin']

    def button_requested(self):
        res = super(AcsLaboratoryRequest, self).button_requested()
        self.filtered(lambda r: r.patient_id.partner_id.phone).action_send_whatsapp()
        return res

    def action_send_whatsapp(self):
        for rec in self:
            if not rec.patient_id.partner_id.phone:
                raise UserError(_("Please Define Mobile Number in Customer."))

            company_id = rec.sudo().company_id or rec.env.user.sudo().company_id
            template = company_id.acs_laboratory_request_template_id
            if rec.patient_id.partner_id.phone and template:
                rendered = self.env['mail.render.mixin']._render_template(template.body_message, rec._name, [rec.id])
                msg = rendered[rec.id]
                rec.send_whatsapp(msg, rec.patient_id.partner_id.phone, rec.patient_id.partner_id, template=template, company_id=company_id.id)
                rec.message_post(body="%s Sent Details by WhatsApp." % (self.env.user.sudo().name))
        return True


class PatientLaboratoryTest(models.Model):
    _name = 'patient.laboratory.test'
    _inherit = ['patient.laboratory.test','acs.whatsapp.mixin']

    def action_done(self):
        res = super(PatientLaboratoryTest, self).action_done()
        self.filtered(lambda r: r.patient_id.partner_id.phone).action_send_whatsapp()
        return res

    def action_send_whatsapp(self):
        for rec in self:
            if not rec.patient_id.partner_id.phone:
                raise UserError(_("Please Define Mobile Number in Customer."))

            company_id = rec.sudo().company_id or rec.env.user.sudo().company_id
            template = company_id.acs_laboratory_result_template_id
            if rec.patient_id.partner_id.phone and template:
                rendered = self.env['mail.render.mixin']._render_template(template.body_message, rec._name, [rec.id])
                msg = rendered[rec.id]
                rec.send_whatsapp(msg, rec.patient_id.partner_id.phone, rec.patient_id.partner_id, template=template, company_id=company_id.id)
                rec.message_post(body="%s Sent Details by WhatsApp." % (self.env.user.sudo().name))
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: