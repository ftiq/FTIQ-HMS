# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AcsNurseWardRound(models.Model):
    _name = 'acs.nurse.ward.round'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Nurse Ward round"

    name = fields.Char(string='Round Number', readonly=True, default='New')
    nurse_id = fields.Many2one('hr.employee', string='Nurse', default=lambda self: self.env.user.employee_id.id, required=True, tracking=1)
    hospitalization_id = fields.Many2one('acs.hospitalization', string='Hospitalization', tracking=1)
    patient_id = fields.Many2one('hms.patient', string='Patient')
    date = fields.Datetime('Date', default=fields.Datetime.now(), required=True, tracking=1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], default='draft', string='Status', tracking=1)

    evaluation_id = fields.Many2one('acs.patient.evaluation', string='Evaluation')
    weight = fields.Float(related="evaluation_id.weight", string='Weight', help="Weight in KG")
    height = fields.Float(related="evaluation_id.height", string='Height', help="Height in cm")
    temp = fields.Float(related="evaluation_id.temp", string='Temp')
    hr = fields.Integer(related="evaluation_id.hr", string='HR', help="Heart Rate")
    rr = fields.Integer(related="evaluation_id.rr", string='RR', help='Respiratory Rate')
    systolic_bp = fields.Integer(related="evaluation_id.systolic_bp", string="Systolic BP")
    diastolic_bp = fields.Integer(related="evaluation_id.diastolic_bp", string="Diastolic BP")
    spo2 = fields.Integer(related="evaluation_id.spo2", string='SpO2', 
        help='Oxygen Saturation, percentage of oxygen bound to hemoglobin')
    rbs = fields.Integer(related="evaluation_id.rbs", string='RBS', readonly=True, 
        help='Random blood sugar measures blood glucose regardless of when you last ate.')
    pain_level = fields.Selection(related="evaluation_id.pain_level", string="Pain Level")
    pain = fields.Selection(related="evaluation_id.pain", string="Pain")
    bmi = fields.Float(related="evaluation_id.bmi", string='Body Mass Index', store=True)
    bmi_state = fields.Selection(related="evaluation_id.bmi_state", string='BMI State', store=True)

    acs_weight_name = fields.Char(related="evaluation_id.acs_weight_name", string='Patient Weight unit of measure label')
    acs_height_name = fields.Char(related="evaluation_id.acs_height_name", string='Patient Height unit of measure label')
    acs_temp_name = fields.Char(related="evaluation_id.acs_temp_name", string='Patient Temp unit of measure label')
    acs_spo2_name = fields.Char(related="evaluation_id.acs_spo2_name", string='Patient SpO2 unit of measure label')
    acs_rbs_name = fields.Char(related="evaluation_id.acs_rbs_name", string='Patient RBS unit of measure label')

    # The Patients of rounding
    position = fields.Boolean(string='Position', 
        help="Check if the patient needs to be repositioned or is unconfortable")
    potty = fields.Boolean(string='Potty', 
        help="Check if the patient needs to urinate / defecate")
    proximity = fields.Boolean(string='Proximity', 
        help="Check if personal items, water, alarm, ... are not in easy reach")
    pump = fields.Boolean(string='Pump', 
        help="Check if there is any issues with the pumps - IVs ... ")
    personal_needs = fields.Boolean(string='Personal Needs', 
        help="Check if the patient requests anything")

    # Diuresis
    diuresis = fields.Integer(string='Diuresis', help="volume in ml")
    urinary_catheter = fields.Boolean(string='Urinary Catheter')

    #Glycemia
    glycemia = fields.Integer(string='Glycemia', help="Blood Glucose level")
    depression = fields.Boolean(string='Depression', help="Check this if the "
        "patient shows signs of depression")
    evolution = fields.Selection([
        ('improving', 'Improving'),
        ('worsening', 'Worsening')], string='Evolution', help="Check your judgement of current"
        "patient condition", default='improving', required=True)
    round_summary = fields.Text(string='Round Summary')
    warning = fields.Boolean(string='Warning', help="Check this box to alert the "
        "supervisor about this patient rounding. A warning icon will be shown in the rounding list")
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)

    @api.model
    def default_get(self, fields):
        res = super(AcsNurseWardRound, self).default_get(fields)
        if self.env.context.get('default_hospitalization_id'):
            res['hospitalization_id'] = self.env.context.get('default_hospitalization_id')
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                seq_date = None
                if vals.get('date'):
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date']))
                vals['name'] = self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code('acs.nurse.ward.round', sequence_date=seq_date) or _("New")
        return super().create(vals_list)

    def action_done(self):
        self.state = "done"

    def action_create_evaluation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.action_acs_patient_evaluation_popup")
        action['domain'] = [('patient_id','=',self.patient_id.id)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_hospitalization_id': self.hospitalization_id.id, 'nurse_ward_round': self.id}
        return action

    @api.onchange('evaluation_id')
    def onchange_evaluation(self):
        if self.evaluation_id:
            self.date = self.evaluation_id.date

    @api.onchange('hospitalization_id')
    def onchange_hospitalization_id(self):
        if self.hospitalization_id:
            self.patient_id = self.hospitalization_id.patient_id.id