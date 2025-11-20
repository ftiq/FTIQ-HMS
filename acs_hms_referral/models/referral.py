# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class HmsReferral(models.Model):
    _name = 'hms.referral'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Referral'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, default='New')
    patient_id = fields.Many2one('hms.patient', string="Patient")
    patient_name = fields.Char(string="Patient Name")
    patient_dob = fields.Date(string="Date of Birth")
    phone = fields.Char(string="Patient Mobile", readonly=True)
    gender = fields.Selection([
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('other', 'Other')], string='Gender', default='male', tracking=True)
    referral_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('hospitalization', 'Hospitalization'),
        ('laboratory', 'Laboratory'),
        ('radiology', 'Radiology'),
        ('pharmacy', 'Pharmacy')
    ], string="Referral Type", required=True, tracking=True)
    referred_physician_id = fields.Many2one('res.partner', string="Referred Physician", tracking=True)
    referring_partner_id = fields.Many2one('res.partner', string="Referred By", readonly=True, default=lambda self: self.env.user.partner_id)
    referred_date = fields.Datetime(string="Referral Date", default=fields.Datetime.now())
    description = fields.Text(string="Description for Referral", required=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('closed', 'Closed')
    ], string="Status", default='active', tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', 'referral_attachment_rel', 'referral_id', 'attachment_id', string="Attachments")
    auto_patient_creation = fields.Boolean(string='Auto Create Patient', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(HmsReferral, self).default_get(fields)
        company = self.env.company
        res['auto_patient_creation'] = company.acs_auto_patient_creation
        return res

    def preview_referral_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': "/acs/my/referrals/%s" % (self.id),
        }
    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)
    
    def _get_portal_return_action(self):
        """ Return the action used to display record when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('acs_hms_referral.action_acs_referral_report')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code('hms.referral') or _("New")
        res = super().create(vals_list)
        return res
    
    def action_closed(self):
        self.state = 'closed'

    def _compute_access_url(self):
        super(HmsReferral, self)._compute_access_url()
        for record in self:
            record.access_url = '/acs/my/referrals/%s' % (record.id)

    def action_create_patient(self):
        self.ensure_one()
        if not self.patient_name:
            raise UserError(_("Patient name is required to create a patient record."))
        if not self.phone:
            raise UserError(_("Patient phone is required to create a patient record."))      
        if not self.gender:
            raise UserError(_("Patient gender is required to create a patient record."))            
        if not self.patient_id:
            Patient = self.env['hms.patient'].sudo().search([
                ('gender', '=', self.gender), 
                ('birthday', 'ilike', self.patient_dob), 
                '|', 
                ('name', 'ilike', self.patient_name), 
                ('phone', 'ilike', self.phone)], limit=1)
            if Patient:
                patient = Patient.id
            else:
                patient_vals = {
                    'name': self.patient_name,
                    'birthday': self.patient_dob,
                    'phone': self.phone,
                    'gender': self.gender,
                }
                patient = self.env['hms.patient'].create(patient_vals)
            self.patient_id = patient

    def acs_close_referrals(self):
        company = self.env.company
        if company.acs_auto_close_referral_days > 0:
            close_date = fields.Date.context_today(self) - timedelta(days=company.acs_auto_close_referral_days)
            referrals_to_close = self.search([('state', '=', 'active'), ('referred_date', '<=', close_date)])
            for referral in referrals_to_close:
                referral.action_closed()

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        for record in self:
            if record.patient_id:
                record.patient_name = record.patient_id.name
                if record.patient_id.phone:
                    record.phone = record.patient_id.phone
                if record.patient_id.birthday:
                    record.patient_dob = record.patient_id.birthday

    @api.ondelete(at_uninstall=False)
    def _unlink_except_active(self):
        for record in self:
            if record.state not in ('active'):
                raise UserError(_("You can delete a record in Active state only."))