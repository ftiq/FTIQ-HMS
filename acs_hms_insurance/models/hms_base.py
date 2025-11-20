# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from ast import literal_eval


class ACSPatient(models.Model):
    _inherit = 'hms.patient'

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        for rec in self:
            rec.claim_count = len(rec.claim_ids)
            rec.insurance_count = len(rec.insurance_ids)

    claim_ids = fields.One2many('hms.insurance.claim', 'patient_id',string='Claims')
    claim_count = fields.Integer(compute='_rec_count', string='# Claims')
    insurance_ids = fields.One2many('hms.patient.insurance', 'patient_id', string='Insurance Policy')
    insurance_count = fields.Integer(compute='_rec_count', string='# Insurance Policy')

    def action_insurance_policy(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_insurance.action_hms_patient_insurance")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id,
        }
        return action

    def action_claim_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_insurance.action_insurance_claim")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id,
        }
        return action


class ACSAppointment(models.Model):
    _inherit = 'hms.appointment'

    insurance_id = fields.Many2one('hms.patient.insurance', string='Insurance Policy', copy=False)
    claim_id = fields.Many2one('hms.insurance.claim', string='Claim', copy=False)
    insurance_company_id = fields.Many2one('hms.insurance.company', related='insurance_id.insurance_company_id', string='Insurance Company', readonly=True, store=True)

    def acs_create_claim_request(self):
        product_data = self.acs_appointment_inv_product_data()
        amount_total = 0
        acs_pricelist_id = self.env.context.get('acs_pricelist_id')
        for line in product_data:
            unit_price = self.with_context(acs_pricelist_id=acs_pricelist_id).acs_product_invoice_amount(line, self.patient_id.partner_id)
            amount_total += line.get('quantity',1) * unit_price

        claim_id = self.env['hms.insurance.claim'].create({
            'patient_id': self.patient_id.id,
            'insurance_id': self.insurance_id.id,
            'claim_for': 'appointment',
            'appointment_id': self.id,
            'amount_requested': amount_total,
        })
        self.claim_id = claim_id.id

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        super(ACSAppointment, self).onchange_patient_id()
        if self.patient_id and self.patient_id.insurance_ids:
            insurance_id = self.patient_id.insurance_ids[0]
            self.insurance_id = insurance_id.id
            self.pricelist_id = insurance_id.pricelist_id and insurance_id.pricelist_id.id or False


class ACSPrescriptionOrder(models.Model):
    _inherit = 'prescription.order'

    insurance_id = fields.Many2one('hms.patient.insurance', string='Insurance Policy', copy=False)
    claim_id = fields.Many2one('hms.insurance.claim', string='Claim', copy=False)
    insurance_company_id = fields.Many2one('hms.insurance.company', related='insurance_id.insurance_company_id', string='Insurance Company', readonly=True, store=True)

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id and self.patient_id.insurance_ids:
            self.insurance_id = self.patient_id.insurance_ids[0].id


class Attachments(models.Model):
    _inherit = "ir.attachment"

    patient_id = fields.Many2one('hms.patient', 'Patient')
    claim_id = fields.Many2one('hms.insurance.claim', 'Claim')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hospital_product_type = fields.Selection(selection_add=[('insurance_plan', 'Insurance Plan')])


class ProductProduct(models.Model):
    _inherit = "product.product"

    def acs_match_product_insurance_rule(self, rule_ids):
        for rule in rule_ids:
            try:
                domain = literal_eval(rule.rule_domain or '[]')
                match = self.search([('id', '=', self.id)] + domain)
            except Exception:
                continue
            if match:
                return rule
    
    def acs_get_product_matching_rule(self, insurance):
        matching_rule = False
        excluded_product_ids = insurance.acs_get_excluded_product_ids()
        if self.id not in excluded_product_ids:
            if insurance.policy_rule_ids:
                matching_rule = self.acs_match_product_insurance_rule(insurance.policy_rule_ids)

            if not matching_rule and insurance.insurance_company_id.policy_rule_ids:
                company_rule_ids = insurance.insurance_company_id.policy_rule_ids.ids
                matching_rule = self.acs_match_product_insurance_rule(company_rule_ids)

        return matching_rule
