# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api,_ ,Command

class PrescriptionOrder(models.Model):
    _inherit = 'prescription.order'

    def acs_get_medication_data(self):
        for record in self:
            record.patient_medication_count = len(record.patient_medication_ids)

    patient_medication_count = fields.Integer(compute='acs_get_medication_data', string='Patient Medication Count')
    patient_medication_ids = fields.One2many('acs.patient.medication', 'prescription_id', string='Patient Medications')

    def create_medication_plan(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_nursing.action_acs_medication_plan_wizard")
        lines = []
        for line in self.prescription_line_ids:
            if line.product_id:
                lines.append(Command.create( {
                    'product_id': line.product_id.id,
                    'dose': line.dose,
                    'dosage_uom_id': line.dosage_uom_id.id,
                    'form_id': line.form_id.id,
                    'route_id': line.route_id.id,
                    'short_comment': line.short_comment,
                    'acs_medication_time_ids': line.product_id.common_dosage_id.acs_medication_time_ids.ids,
                    'days': line.days or 1.0
                }))
        action['context'] = {'default_prescription_id': self.id, 'default_hospitalization_id': self.hospitalization_id.id, 'default_physician_id': self.physician_id.id, 'default_line_ids': lines}
        return action

    def action_patient_medication(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_nursing.hms_acs_patient_medication_action")
        action['domain'] = [('prescription_id','=',self.id)]
        action['context'] = {'default_prescription_id': self.id, 'default_physician_id': self.physician_id.id, 'default_patient_id': self.patient_id.id , 'default_hospitalization_id': self.hospitalization_id.id or False}
        return action


class HmsHospitalization(models.Model):
    _inherit = 'acs.hospitalization'

    def acs_get_hospitalization_count(self):
        for record in self:
            record.ward_round_count = len(record.ward_round_ids)
            record.patient_medication_count = len(record.patient_medication_ids)

    ward_round_count = fields.Integer(compute='acs_get_hospitalization_count', string='Ward Round Count')
    ward_round_ids = fields.One2many('acs.nurse.ward.round', 'hospitalization_id', string='Ward Rounds')

    patient_medication_count = fields.Integer(compute='acs_get_hospitalization_count', string='Patient Medication Count')
    patient_medication_ids = fields.One2many('acs.patient.medication', 'hospitalization_id', string='Patient Medications')

    def acs_hospitalization_nurse_round_data(self, invoice_id=False):
        product_data = []
        ward_rounds_to_invoice = self.ward_round_ids.filtered(lambda s: not s.invoice_id)
        if ward_rounds_to_invoice:
            ward_data = {}
            for ward_round in ward_rounds_to_invoice:
                if ward_round.nurse_id.ward_round_product_id:
                    if ward_round.nurse_id.ward_round_product_id in ward_data:
                        ward_data[ward_round.nurse_id.ward_round_product_id] += 1
                    else:
                        ward_data[ward_round.nurse_id.ward_round_product_id] = 1
            if ward_data:
                product_data.append({
                    'name': _("Nurse Ward Round Charges"),
                    'display_type': 'line_section'
                })
                # Forward display_type so acs_create_invoice_line can render the invoice layout correctly
            for product in ward_data:
                product_data.append({
                    'product_id': product,
                    'quantity': ward_data[product],
                    'acs_hms_source_type': 'hospitalization',
                    'acs_hospitalization_ids': [self.id]
                })

            if invoice_id:
                ward_rounds_to_invoice.invoice_id = invoice_id.id
        return product_data
    
    def create_medication_plan(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_nursing.action_acs_medication_plan_wizard")
        action['context'] = {'default_hospitalization_id': self.id, 'default_physician_id': self.physician_id.id, 'default_patient_id': self.patient_id.id}
        return action

    def action_view_wardrounds(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_nursing.hms_ward_round_action")
        action['domain'] = [('hospitalization_id','=',self.id)]
        action['context'] = {'default_hospitalization_id': self.id, 'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id}
        return action

    def action_patient_medication(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_nursing.hms_acs_patient_medication_action")
        action['domain'] = [('hospitalization_id','=',self.id)]
        action['context'] = {'default_hospitalization_id': self.id, 'default_physician_id': self.physician_id.id, 'default_patient_id': self.patient_id.id}
        return action


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ward_round_product_id = fields.Many2one('product.product', domain=[('type','=','service')],
        string='Ward Round Service',  ondelete='cascade', help='Registration Product')
    

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    ward_round_product_id = fields.Many2one('product.product', domain=[('type','=','service')],
        string='Ward Round Service',  ondelete='cascade', help='Registration Product')


class AcsPatientEvaluation(models.Model):
    _inherit = 'acs.patient.evaluation'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            if self.env.context.get('nurse_ward_round'):
                ward_round = self.env['acs.nurse.ward.round'].browse(self.env.context.get('nurse_ward_round'))
                ward_round.write({'evaluation_id': record.id})
        return res


class AcsHmsPatient(models.Model):
    _inherit = 'hms.patient'

    def _rec_count(self):
        rec = super(AcsHmsPatient, self)._rec_count()
        for rec in self:
            rec.patient_medication_count = len(rec.patient_medication_ids)

    patient_medication_count = fields.Integer(compute='_rec_count', string='Patient Medication Count')
    patient_medication_ids = fields.One2many('acs.patient.medication', 'hospitalization_id', string='Patient Medications')

    def action_patient_medication(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_nursing.hms_acs_patient_medication_action")
        action['domain'] = [('patient_id','=',self.id)]
        return action