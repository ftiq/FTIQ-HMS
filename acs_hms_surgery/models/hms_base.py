# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models,_, Command

class HmsPrescription(models.Model):
    _inherit = "prescription.order"

    surgery_id = fields.Many2one('hms.surgery', string='Surgery')


class ACSPrescriptionLine(models.Model):
    _inherit = 'prescription.line'
    
    surgery_template_id = fields.Many2one('hms.surgery.template', ondelete="cascade", string='Surgery Template')
    surgery_id = fields.Many2one('hms.surgery', ondelete="cascade", string='Surgery')


class ACSAppointment(models.Model):
    _inherit = 'hms.appointment'

    def _rec_surgery_count(self):
        for rec in self:
            rec.surgery_count = len(rec.surgery_ids)

    surgery_ids = fields.One2many('hms.surgery', 'appointment_id', string='Surgeries', groups="acs_hms_surgery.group_acs_hms_surgery_user")
    surgery_count = fields.Integer(compute='_rec_surgery_count', string='# Surgeries', groups="acs_hms_surgery.group_acs_hms_surgery_user")

    def action_view_surgery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_surgery.action_hms_surgery")
        action['domain'] = [('id','in',self.surgery_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_primary_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        return action

    #Method to collect common invoice related records data
    def acs_appointment_common_data(self, invoice_id):
        data = super().acs_appointment_common_data(invoice_id)
        surgery_ids = self.sudo().surgery_ids.filtered(lambda s: not s.invoice_id)
        data += surgery_ids.acs_common_invoice_surgery_data(invoice_id)
        return data
    
    def get_acs_show_create_invoice(self):
        super().get_acs_show_create_invoice()
        for rec in self:
            if rec.surgery_ids:
                uninvoiced_surgeries = rec.surgery_ids.filtered(lambda s: not s.invoice_id)
                if uninvoiced_surgeries:
                    rec.acs_show_create_invoice = True
                else:
                    rec.acs_show_create_invoice = False

class HmsTreatment(models.Model):
    _inherit = 'hms.treatment'

    def action_view_surgery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_surgery.action_hms_surgery")
        action['domain'] = [('treatment_id', '=', self.id)]
        action['context'] = {'default_treatment_id': self.id, 'default_patient_id': self.patient_id.id}
        return action


class ACSPatient(models.Model):
    _inherit = "hms.patient"

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        for rec in self:
            rec.surgery_count = len(rec.sudo().surgery_ids)

    surgery_ids = fields.One2many('hms.surgery', 'patient_id', string='Surgery', groups="acs_hms_surgery.group_acs_hms_surgery_user")
    surgery_count = fields.Integer(compute='_rec_count', string='# Surgery', groups="acs_hms_surgery.group_acs_hms_surgery_user")
    past_surgeries_ids = fields.One2many('past.surgeries', 'patient_id', string='Past Surgeries')

    def action_view_surgery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_surgery.action_hms_surgery")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action


class ACSConsumableLine(models.Model):
    _inherit = "hms.consumable.line"

    surgery_template_id = fields.Many2one('hms.surgery.template', ondelete="cascade", string='Surgery Template')
    surgery_id = fields.Many2one('hms.surgery', ondelete="cascade", string='Surgery')


class StockMove(models.Model):
    _inherit = "stock.move"

    surgery_id = fields.Many2one('hms.surgery', string='Surgery')


class product_template(models.Model):
    _inherit = "product.template"

    hospital_product_type = fields.Selection(selection_add=[('surgery', 'Surgery')])


class Physician(models.Model):
    _inherit = "hms.physician"

    def _rec_sur_count(self):
        Surgery = self.env['hms.surgery']
        for record in self.with_context(active_test=False):
            record.surgery_count = Surgery.search_count([('primary_physician_id', '=', record.id)])

    surgery_count = fields.Integer(compute='_rec_sur_count', string='# Surgery', groups="acs_hms_surgery.group_acs_hms_surgery_user")

    def action_surgery_physician(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_surgery.action_hms_surgery")
        action['domain'] = [('primary_physician_id','=',self.id)]
        action['context'] = {'default_primary_physician_id': self.id}
        return action

class ACSHmsMixin(models.AbstractModel):
    _inherit = "acs.hms.mixin"

    # MKA: Once the invoice is created from the surgery even from, hospitalization, 
    # The Record will be linked to its corresponding records invoice line.
    def acs_prepare_invoice_line_data(self, data, inv_data={}, fiscal_position_id=False):
        res = super().acs_prepare_invoice_line_data(data, inv_data, fiscal_position_id)
        if data.get('acs_hms_source_type') == 'surgery' and data.get('acs_surgery_ids'):
            res['acs_surgery_ids'] = [Command.set(data.get('acs_surgery_ids', [self.id]))]
        return res