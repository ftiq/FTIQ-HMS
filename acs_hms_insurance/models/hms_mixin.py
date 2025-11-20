# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from ast import literal_eval


class ACSHmsMixin(models.AbstractModel):
    _inherit = "acs.hms.mixin"

    #ACS: Replace code 
    @api.model
    def acs_create_invoice(self, partner, patient=False, product_data=[], inv_data={}):
        create_insurance_invoice = False
        #Check if insurance module is installed.
        installed_acs_hms_insurance = self.env['ir.module.module'].sudo().search([('name','=','acs_hms_insurance'),('state','=','installed')])
        #insurance invoice only if delivered.
        if hasattr(self, 'insurance_id'):
            if self._name != 'prescription.order' and self.insurance_id:
                create_insurance_invoice = True
            elif (
                self._name == 'prescription.order'
                and installed_acs_hms_insurance
                and getattr(self, 'delivered', False)
                and self.insurance_id
            ):
                # need sudo if prescription.order and delivered
                self = self.sudo()
                create_insurance_invoice = True

        # Create the invoice
        if create_insurance_invoice:
            return self.acs_create_insurance_invoices(partner, patient, product_data, inv_data)
        return self._acs_create_invoice(partner, patient, product_data, inv_data)

    def acs_create_insurance_invoices(self, partner, patient=False, product_data=[], inv_data={}):
        insurance_id = self.insurance_id
        main_product_data = product_data
        insurance_inv_data = inv_data.copy()
        patient_product_data = []
        insurance_product_data = []
        insurance_partner_id = insurance_id.insurance_company_id.partner_id if insurance_id.insurance_company_id.partner_id else partner
        insurance_inv_data.update({
            'partner_id': insurance_partner_id,
            'patient_id': inv_data.get('patient_id'),
        })
        # ---- Track rule totals here ----
        rule_data = {}   # {rule_id: {'covered': 0.0, 'limit': x, 'copay': y, 'rule': rule_rec}}

        for line_data in main_product_data:
            product = line_data.get('product_id')
            patient_line_data = line_data.copy()
            insurance_line_data = line_data.copy()

            if product:
                quantity = line_data.get('quantity', 1.0)
                unit_price = self.acs_product_invoice_amount(line_data, partner)
                total_price = unit_price * quantity
                insurance_cover = 0.0
                patient_payable_total = total_price

                matching_rule = product.acs_get_product_matching_rule(insurance_id)
                if matching_rule:
                    # prepare dict entry for this rule if not present
                    if matching_rule.id not in rule_data:
                        rule_data[matching_rule.id] = {
                            'covered': 0.0,
                            'limit': matching_rule.limit or 0.0,
                            'copay': matching_rule.copay or 0.0,
                            'rule': matching_rule,
                        }

                    # calculate requested coverage
                    requested = (
                        total_price * (matching_rule.percentage / 100.0)
                        if matching_rule.rule_type == 'percentage'
                        else matching_rule.amount
                    )

                    # check remaining limit for this rule
                    limit = rule_data[matching_rule.id]['limit']
                    if limit:
                        remaining = max(limit - rule_data[matching_rule.id]['covered'], 0.0)
                        requested = min(requested, remaining)

                    insurance_cover = requested
                    patient_payable_total = total_price - insurance_cover

                    # add to running total for this rule
                    rule_data[matching_rule.id]['covered'] += insurance_cover

                # add copay (flat amount per line, not per unit)
                if matching_rule and matching_rule.copay:
                    patient_payable_total += matching_rule.copay

                # convert back to per-unit price for invoice
                insurance_line_data.update({
                    'price_unit': insurance_cover / quantity if quantity else 0.0,
                    'acs_patient_amount': patient_payable_total / quantity if quantity else 0.0,
                    'quantity': quantity,
                })
                patient_line_data.update({
                    'price_unit': patient_payable_total / quantity if quantity else 0.0,
                    'acs_insurance_amount': insurance_cover / quantity if quantity else 0.0,
                    'quantity': quantity,
                })

            patient_product_data.append(patient_line_data)
            insurance_product_data.append(insurance_line_data)
            
        insurance_invoice = self._acs_create_invoice(insurance_partner_id, patient, insurance_product_data, inv_data)
        patient_invoice = self._acs_create_invoice(partner, patient, patient_product_data, inv_data)
        claim_id = False
        
        if insurance_id.create_claim:
            claim_for_mapping = {'hms.appointment': 'appointment', 'acs.hospitalization': 'hospitalization',
                        'hms.surgery': 'surgery', 'patient.laboratory.test': 'laboratory',
                        'patient.radiology.test': 'radiology', 'patient.laboratory.test': 'laboratory',
                        'prescription.order': 'pharmacy'}
        
            claim_field_name = {'hms.appointment': 'appointment_id', 'acs.hospitalization': 'hospitalization_id',
                            'hms.surgery': 'surgery_id', 'patient.laboratory.test': 'laboratory_request_id',
                            'patient.radiology.test': 'radiology_request_id', 
                            'prescription.order': 'prescription_id'}
                            
            claim_data = {
                'patient_id': patient.id,
                'insurance_id': insurance_id.id,
                'claim_for': claim_for_mapping.get(self._name,'other'),
                'amount_requested': insurance_invoice.amount_total,
            }
            claim_field = claim_field_name.get(self._name,False)
            if claim_field:
                claim_data[claim_field] = self.id
            claim_id = self.env['hms.insurance.claim'].create(claim_data)
            self.claim_id = claim_id.id

        insurance_invoice.write({
            'insurance_id': insurance_id.id, 
            'patient_invoice_id': patient_invoice.id,
            'claim_id': claim_id.id if claim_id else False,
        })
        patient_invoice.write({
            'insurance_id': insurance_id.id, 
            'insurance_invoice_id': insurance_invoice.id,
            'claim_id': claim_id.id if claim_id else False,
        })
        return patient_invoice
