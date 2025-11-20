# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, Command
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import datetime

import base64
from io import BytesIO


class ResPartner(models.Model):
    _inherit= "res.partner"

    #ACS Note: Adding assignee as relation with partner for receptionist or Doctor to access only those patients assigned to them
    assignee_ids = fields.Many2many('res.partner','acs_partner_asignee_relation','partner_id','assigned_partner_id','Assignees', help='Assigned partners for receptionist or doctor etc to see the records')


class HospitalDepartment(models.Model):
    _inherit = 'hr.department'

    note = fields.Text('Note')
    patient_department = fields.Boolean("Patient Department", default=True)
    appointment_ids = fields.One2many("hms.appointment", "department_id", "Appointments")
    department_type = fields.Selection([('general','General'),('nurse', 'Nurse')], string="Hospital Department")
    consultation_service_id = fields.Many2one('product.product', ondelete='restrict', string='Consultation Service')
    followup_service_id = fields.Many2one('product.product', ondelete='restrict', string='Followup Service')
    image = fields.Binary(string='Image')


class ACSEthnicity(models.Model):
    _description = "Ethnicity"
    _name = 'acs.ethnicity'

    name = fields.Char(string='Name', required=True ,translate=True)
    code = fields.Char(string='Code')
    notes = fields.Char(string='Notes')

    _name_uniq = models.Constraint(
        'UNIQUE(name)',
        "Name must be unique!",
    )


class ACSMedicalAlert(models.Model):
    _name = 'acs.medical.alert'
    _description = "Medical Alert for Patient"

    name = fields.Char(required=True)
    description = fields.Text('Description')
    
    
class ACSAllergies(models.Model):
    _name = 'acs.medical.allergy'
    _description = "Allergies for Patient"

    name = fields.Char(required=True)
    description = fields.Text('Description')


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    birthday = fields.Date('Date of Birth')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hospital_product_type = fields.Selection(selection_add=[('procedure', 'Procedure'), ('consultation','Consultation')])
    common_dosage_id = fields.Many2one('medicament.dosage', ondelete='cascade',
        string='Frequency', help='Drug form, such as tablet or gel')
    manual_prescription_qty = fields.Boolean("Manual Prescription Qty")
    procedure_time = fields.Float("Procedure Time")
    appointment_invoice_policy = fields.Selection([('at_end','Invoice in the End'),
        ('anytime','Invoice Anytime'),
        ('advance','Invoice in Advance'),
        ('foc','No Invoice')], string="Appointment Invoicing Policy")
    acs_allow_substitution = fields.Boolean(string='Allow Substitution')
    short_comment = fields.Char(string='Comment', help='Short comment on the specific drug')


class ACSConsumableLine(models.Model):
    _inherit = "hms.consumable.line"

    appointment_id = fields.Many2one('hms.appointment', ondelete="cascade", string='Appointment')
    procedure_id = fields.Many2one('acs.patient.procedure', ondelete="cascade", string="Procedure")
    procedure_group_id = fields.Many2one('procedure.group.line', ondelete="cascade", string="Procedure Group")
    move_ids = fields.Many2many('stock.move', 'consumable_line_stock_move_rel', 'move_id', 'consumable_id', 'Kit Stock Moves', readonly=True)
    #ACS: In case of kit moves set move_ids but add move_id also. Else it may lead to consume material process again.

class Physician(models.Model):
    _inherit = 'hms.physician'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            if not record.is_portal_user:
                record.group_ids = [Command.link( self.env.ref('acs_hms.group_hms_jr_doctor').id)]
        return res

class ACSHmsMixin(models.AbstractModel):
    _inherit = "acs.hms.mixin"

    def acs_prepare_invoice_line_data(self, data, inv_data={}, fiscal_position_id=False):
        res = super().acs_prepare_invoice_line_data(data, inv_data, fiscal_position_id)
        if data.get('acs_hms_source_type') == 'appointment' and data.get('acs_appointment_ids'):
            res['acs_appointment_ids'] = [Command.set(data.get('acs_appointment_ids', [self.id]))]

        if data.get('acs_hms_source_type') == 'procedure' and data.get('acs_procedure_ids'):
            res['acs_procedure_ids'] = [Command.set(data.get('acs_procedure_ids'))]
        
        if data.get('acs_hms_source_type') == 'treatment' and data.get('acs_treatment_ids'):
            res['acs_treatment_ids'] = [Command.set(data.get('acs_treatment_ids'))]
        return res