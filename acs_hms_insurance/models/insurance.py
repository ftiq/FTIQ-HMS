# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AcsInsurancePlan(models.Model):
    _name = 'acs.insurance.plan'
    _description = "Insurance Plan"
    _order = "sequence"

    name = fields.Text(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string="Active", default=True)
    insurance_company_id = fields.Many2one('hms.insurance.company', string ="Insurance Company", required=True)
    create_claim = fields.Boolean(string="Appointment Create Claim")    
    policy_rule_ids = fields.One2many("acs.insurance.policy.rule", "insurance_plan_id", string="Policy Patient Share Rules")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',
        help="If you change the pricelist, only newly added lines will be affected.")
    note = fields.Text("Notes")
    excluded_product_ids = fields.Many2many('product.template', 'acs_product_template_insurance_plan_rel', 'plan_id', 'product_id', string="Excluded Products")


class AcsInsurancePolicyRules(models.Model):
    _name = 'acs.insurance.policy.rule'
    _description = 'Patient Share Rules'
    _order = "sequence"

    sequence = fields.Integer(string='Sequence', default=50)
    insurance_company_id = fields.Many2one('hms.insurance.company', string ="Insurance Company")
    insurance_policy_id = fields.Many2one('hms.patient.insurance', string ="Insurance Policy")
    insurance_plan_id = fields.Many2one('acs.insurance.plan', string ="Insurance Plan")
    rule_domain = fields.Char(string='Apply On', compute_sudo=True)
    rule_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('amount', 'Amount'), 
    ], string='Type', default='percentage')
    percentage = fields.Float('Percentage')
    amount = fields.Float('Amount')
    copay = fields.Float('Co-Payment')
    limit = fields.Float('Limit')
    full_cover = fields.Boolean(string="100%")
    description = fields.Text("Description")

    @api.constrains('rule_type','percentage','amount')
    def _check_allocation(self):
        for rec in self:
            if rec.rule_type=='percentage' and rec.full_cover:
                pass
            elif rec.rule_type=='percentage' and (rec.percentage>100 or rec.percentage<=0):
                raise ValidationError((_("Percentage can not be more than 100 or zero.")))
            elif rec.rule_type=='amount' and (rec.amount<0):
                raise ValidationError((_("Amount can not be negative.")))

    @api.onchange('full_cover')
    def onchange_full_cover(self):
        if self.full_cover:
            self.percentage = 100


class InsuranceCompany(models.Model):
    _name = 'hms.insurance.company'
    _description = "Insurance Company"
    _inherits = {
        'res.partner': 'partner_id',
    }
    
    description = fields.Text()
    partner_id = fields.Many2one('res.partner', 'Partner', ondelete='restrict', required=True)
    active = fields.Boolean(string="Active", default=True)
    policy_rule_ids = fields.One2many("acs.insurance.policy.rule", "insurance_company_id", string="Policy Patient Share Rules")
    excluded_product_ids = fields.Many2many('product.template', 'acs_product_template_insurance_company_rel', 'insurance_company_id', 'product_id', string="Excluded Products")

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            self.name = self.partner_id.name

    #ACS NOTE: To avoid dependency issue this code is here. 
    #Move to related module if new one is created.
    @api.model
    def GetInsuranceCompany(self, args, **kwargs):
        """
        var model = 'hms.insurance.company';
        var method = 'GetInsuranceCompany';

        var args = [
            { }
        ];
        """
        insurance_companies = self.sudo().search([])
        insurance_company_data = []
        for ic in insurance_companies:
            insurance_company_data.append({
                'id': ic.id,
                'name': ic.name,
            })
        return insurance_company_data


class Insurance(models.Model):
    _name = 'hms.patient.insurance'
    _description = "Patient Insurance"
    _rec_name = 'policy_number'
    
    patient_id = fields.Many2one('hms.patient', string ='Patient', ondelete='restrict', required=True)
    insurance_company_id = fields.Many2one('hms.insurance.company', string ="Insurance Company", required=True)
    insurance_plan_id = fields.Many2one('acs.insurance.plan', string ="Insurance Plan")
    policy_number = fields.Char(string ="Policy Number", required=True)
    insured_value = fields.Float(string ="Insured Value")
    validity = fields.Date(string="Validity")
    active = fields.Boolean(string="Active", default=True)
    note = fields.Text("Notes")
    create_claim = fields.Boolean(string="Create Claim")

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',
        help="If you change the pricelist, only newly added lines will be affected.")
    company_id = fields.Many2one('res.company', 'Hospital', default=lambda self: self.env.company)
    insurance_amount_in_invoice = fields.Boolean("Show Insurance Amounts in Invoice", default=True)
    policy_rule_ids = fields.One2many("acs.insurance.policy.rule", "insurance_policy_id", string="Policy Patient Share Rules")
    excluded_product_ids = fields.Many2many('product.template', 'acs_product_template_policy_rel', 'policy_id', 'product_id', string="Excluded Products")
    insured_card_number = fields.Char(string='Insured Card ID Number', help="The identification number on the patient's insurance card.")

    def _compute_display_name(self):
        for rec in self:
            name = rec.policy_number 
            if rec.insurance_plan_id:
                name += ' - ' + rec.insurance_plan_id.name
            elif rec.insurance_company_id:
                name += ' - ' + rec.insurance_company_id.name
            rec.display_name = name

    @api.onchange('insurance_company_id')
    def onchange_insurance_company(self):
        if self.insurance_company_id and self.insurance_company_id.property_product_pricelist:
            self.pricelist_id = self.insurance_company_id.property_product_pricelist.id
        if self.insurance_company_id and self.insurance_company_id.excluded_product_ids:
            self.excluded_product_ids = self.insurance_company_id.excluded_product_ids

    @api.onchange('insurance_plan_id')
    def onchange_insurance_plan(self):
        if self.insurance_plan_id:
            self.policy_rule_ids.unlink()
            plan_id = self.insurance_plan_id
            policy_rule_lines = []
            for line in plan_id.policy_rule_ids:
                policy_rule_lines.append((0,0,{
                    'sequence': line.sequence,
                    'rule_domain': line.rule_domain,
                    'rule_type' : line.rule_type,
                    'percentage': line.percentage,
                    'amount': line.amount,
                    'full_cover': line.full_cover,
                    'copay': line.copay,
                    'limit': line.limit,
                    'description': line.description,
                }))
            self.pricelist_id = plan_id.pricelist_id and plan_id.pricelist_id.id
            self.create_claim = plan_id.create_claim
            self.policy_rule_ids = policy_rule_lines
            self.excluded_product_ids = plan_id.excluded_product_ids

    @api.model
    def archive_expired_policy(self):
        records = self.search([('validity','<', fields.Date.today())])
        records.write({'active': False})

    def acs_get_excluded_product_ids(self):
        excluded_product_ids = []
        for rec in self:
            excluded_product_ids += rec.excluded_product_ids.mapped('product_variant_ids').ids
            if rec.insurance_company_id and rec.insurance_company_id.excluded_product_ids:
                excluded_product_ids += rec.insurance_company_id.excluded_product_ids.mapped('product_variant_ids').ids
        return excluded_product_ids


class InsuranceTPA(models.Model):
    _name = 'insurance.tpa'
    _description = "Insurance TPA"
    _inherits = {
        'res.partner': 'partner_id',
    }

    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete='restrict')
    active = fields.Boolean('Active', default=True)


class InsuranceChecklistTemp(models.Model):
    _name = 'hms.insurance.checklist.template'
    _description = "Insurance Checklist Template"

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)


class RequiredDocuments(models.Model):
    _name = 'hms.insurance.req.doc'
    _description = "Insurance Req Doc"
    
    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)


class InsuranceCheckList(models.Model):
    _name="hms.insurance.checklist"
    _description = "Insurance Checklist"

    name = fields.Char(string="Name")
    is_done = fields.Boolean(string="Y/N")
    remark = fields.Char(string="Remarks")
    claim_id = fields.Many2one("hms.insurance.claim", string="Claim")
