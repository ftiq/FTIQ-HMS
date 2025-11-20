# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class HmsAppointment(models.Model):
    _name = "hms.appointment"
    _inherit = ['portal.mixin', 'hms.appointment']

    def get_acs_access_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            if not rec.access_token:
                rec._portal_ensure_token()
            rec.acs_access_url = '%s/my/appointments/%s?access_token=%s' % (base_url, rec.id, rec.access_token)

    def _compute_access_url(self):
        super(HmsAppointment, self)._compute_access_url()
        for record in self:
            record.access_url = '/my/appointments/%s' % (record.id)

    def acs_preview_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }


class PrescriptionOrder(models.Model):
    _name = "prescription.order"
    _inherit = ['portal.mixin', 'prescription.order']

    def _compute_access_url(self):
        super(PrescriptionOrder, self)._compute_access_url()
        for record in self:
            record.access_url = '/my/prescriptions/%s' % (record.id)

    def acs_preview_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }


class AcsPatientEvaluation(models.Model):
    _name = "acs.patient.evaluation"
    _inherit = ['portal.mixin', 'acs.patient.evaluation']

    def _compute_access_url(self):
        super(AcsPatientEvaluation, self)._compute_access_url()
        for record in self:
            record.access_url = '/my/evaluations/%s' % (record.id)

    def acs_preview_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
