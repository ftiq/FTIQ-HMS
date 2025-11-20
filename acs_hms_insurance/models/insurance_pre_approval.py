# -*- encoding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date 

class AcsInsurancePreApproval(models.Model):
    _name = 'acs.insurance.pre.approval'
    _description = 'Insurance Pre-Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, default="New", tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('resubmitted', 'Resubmitted')
    ], string='Status', default='draft', tracking=True)

    acs_patient_id = fields.Many2one('hms.patient', 'Patient', required=True)
    acs_patient_age = fields.Char(string='Age', store=True)

    acs_relative_contact_number = fields.Char(string='Contact number of attending Relative')
    acs_insured_card_number = fields.Char(string='Insured Card ID Number')
    acs_policy_number = fields.Char(string='Policy Number/Name of Corporate', tracking=True)
    acs_employee_id = fields.Char(string='Employee ID')
    acs_other_mediclaim = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Currently have any other mediclaim/health insurance?')
    acs_other_mediclaim_company_name = fields.Many2one('hms.insurance.company', string='Company Name (Other Mediclaim)')
    acs_other_mediclaim_details = fields.Text(string='Details (Other Mediclaim)')
    acs_family_physician = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Do you have a family Physician?')
    acs_family_physician_name = fields.Char(string='Name of the Family Physician')
    acs_patient_current_address = fields.Text(string='Current Address of Insured Patient')
    acs_patient_occupation = fields.Char(string='Occupation of Insured Patient')

    acs_illness_nature = fields.Text(string='Nature of Illness/Disease with presenting complaint')
    acs_critical_findings = fields.Text(string='Relevant Critical Findings')
    acs_ailment_duration_days = fields.Integer(string='Duration of the present ailment (Days)')
    acs_first_consultation_date = fields.Date(string='i. Date of First consultation')
    acs_past_ailment_history = fields.Text(string='ii. Past history of present ailment, if any')
    acs_provisional_diagnosis = fields.Text(string='Provisional diagnosis')
    acs_icd10_code = fields.Char(string='ICD 10 code')
    acs_proposed_treatment_medical = fields.Boolean(string='Medical Management')
    acs_proposed_treatment_surgical = fields.Boolean(string='Surgical Management')
    acs_proposed_treatment_intensive_care = fields.Boolean(string='Intensive care')
    acs_proposed_treatment_investigation = fields.Boolean(string='Investigation')
    acs_proposed_treatment_non_allopathic = fields.Boolean(string='Non-allopathic treatment')
    acs_investigation_medical_details = fields.Text(string='Investigation and/or Medical Management details')
    acs_drug_administration_route = fields.Char(string='Route of Drug Administration')
    acs_icd10_pcs_code = fields.Char(string='ICD 10 PCS code')
    acs_other_treatment_details = fields.Text(string='If other treatment, provide details')
    acs_how_injury_occurred = fields.Text(string='How did injury occur')
    acs_substance_abuse_alcohol = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Injury/Disease caused due to substance abuse/Alcohol consumption?')
    acs_test_conducted_substance_abuse = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Test conducted to establish this (if yes, attach report)')
    acs_maternity_g = fields.Integer(string='G')
    acs_maternity_p = fields.Integer(string='P')
    acs_maternity_l = fields.Integer(string='L')
    acs_maternity_a = fields.Integer(string='A')
    acs_expected_delivery_date = fields.Date(string='Expected date of Delivery')

    acs_hospitalization_event_type = fields.Selection([('emergency', 'Emergency'), ('planned', 'Planned')], string='Is this an emergency/planned hospitalization event?')

    acs_has_chronic_diabetes = fields.Boolean(string='Diabetes')
    acs_chronic_diabetes = fields.Integer(string='Diabetes (Since Year)')

    acs_has_chronic_heart_disease = fields.Boolean(string='Heart Disease')
    acs_chronic_heart_disease = fields.Integer(string='Heart Disease (Since Year)')

    acs_has_chronic_hypertension = fields.Boolean(string='Hypertension')
    acs_chronic_hypertension = fields.Integer(string='Hypertension (Since Year)')

    acs_has_chronic_hyperlipidemias = fields.Boolean(string='Hyperlipidemias')
    acs_chronic_hyperlipidemias = fields.Integer(string='Hyperlipidemias (Since Year)')

    acs_has_chronic_osteoarthritis = fields.Boolean(string='Osteoarthritis')
    acs_chronic_osteoarthritis = fields.Integer(string='Osteoarthritis (Since Year)')

    acs_has_chronic_asthma_copd_bronchitis = fields.Boolean(string='Asthma/COPD/Bronchitis')
    acs_chronic_asthma_copd_bronchitis = fields.Integer(string='Asthma/COPD/Bronchitis (Since Year)')

    acs_has_chronic_cancer = fields.Boolean(string='Cancer')
    acs_chronic_cancer = fields.Integer(string='Cancer (Since Year)')

    acs_has_chronic_alcohol_drug_abuse = fields.Boolean(string='Alcohol/Drug abuse')
    acs_chronic_alcohol_drug_abuse = fields.Integer(string='Alcohol/Drug abuse (Since Year)')

    acs_has_chronic_hiv_std = fields.Boolean(string='HIV/STD related ailment')
    acs_chronic_hiv_std = fields.Integer(string='Any HIV/or STD related ailment (Since Year)')

    acs_has_chronic_other_ailment = fields.Boolean(string='Any other ailment')
    acs_chronic_other_ailment_details = fields.Text(string='Any other ailment, give details') # This remains Text

    acs_expected_stay_days = fields.Integer(string='Expected number of Days/Stay in hospital')
    acs_icu_days = fields.Integer(string='Days in ICU')
    acs_room_type = fields.Char(string='Room Type')
    acs_per_day_room_rent = fields.Float(string='Per day room rent + nursing and service charges + patients diet')
    acs_expected_investigation_cost = fields.Float(string='Expected cost of investigation + diagnostic')
    acs_icu_charges = fields.Float(string='ICU charges')
    acs_ot_charges = fields.Float(string='OT charges')
    acs_professional_fees = fields.Float(string='Professional fees Surgeon + Anesthetist Fees + consultation charges')
    acs_medicines_consumables_implants = fields.Float(string='Medicines + Consumables + Cost of Implants (if applicable please specify)')
    acs_other_hospital_expenses = fields.Float(string='Other hospital expenses if any')
    acs_all_inclusive_package_charges = fields.Float(string='All-inclusive package charges if any applicable')
    acs_sum_total_expected_cost = fields.Float(string='Sum Total expected cost of hospitalization', tracking=True)

    acs_declaration_doctor_registration = fields.Char(string='Registration number with state code')

    acs_doctor_signature = fields.Binary(string="Patient/Insured Name and Signature", attachment=True)

    acs_patient_declaration_date = fields.Date(string="Date of Declaration")
    acs_patient_declaration_time = fields.Float(string="Time of Declaration")

    acs_requested_amount = fields.Float(string='Requested Amount', compute='_compute_acs_requested_amount', store=True, tracking=True)
    acs_approved_amount = fields.Float(string='Approved Amount', tracking=True)
    acs_approval_date = fields.Date(string='Approval Date')
    acs_approver_user_id = fields.Many2one('res.users', string='Approver')
    acs_denial_reason = fields.Text(string='Denial Reason')
    acs_comments = fields.Text(string='Internal Comments')
    acs_insurance_claim_id = fields.Many2one('hms.insurance.claim', string='Insurance Claim')
    acs_treating_doctor = fields.Many2one('hms.physician', string='Name of the treating doctor', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code('acs.insurance.pre.approval') or _("New")
        return super().create(vals_list)

    @api.onchange('acs_insurance_claim_id')
    def acs_onchange_patient_details_from_claim(self):
        for rec in self:
            rec.acs_patient_id = rec.acs_insurance_claim_id.patient_id.id
            rec.acs_patient_age = rec.acs_insurance_claim_id.patient_id.age
            rec.acs_policy_number = rec.acs_insurance_claim_id.insurance_id.policy_number
        
    @api.depends('acs_sum_total_expected_cost')
    def _compute_acs_requested_amount(self):
        for record in self:
            record.acs_requested_amount = record.acs_sum_total_expected_cost
    
    def action_submit(self):
        for rec in self:
            rec.state = 'submitted'

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'
            rec.acs_approval_date = fields.Date.today()
            rec.acs_approver_user_id = self.env.user

    def action_deny(self):
        for rec in self:
            rec.state = 'denied'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
