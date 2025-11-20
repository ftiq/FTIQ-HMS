# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pytz
from pytz import timezone, utc
from odoo.tools.float_utils import float_round
from datetime import date, datetime, timedelta


class AcsMedicationTime(models.Model):
    _name = 'acs.medication.time'
    _description = "Medication Time"
    _order = "sequence"

    @api.depends('acs_time')
    def acs_get_name(self):
        for rec in self:
            name = '/'
            if rec.acs_time:
                hours = int(rec.acs_time)
                minutes = int(round((rec.acs_time - hours) * 60))
                name = f"{hours:02d}:{minutes:02d}"
            rec.name = name

    name = fields.Char(string='name', compute='acs_get_name')
    acs_time = fields.Float(string='Time', required=True, index=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Char(string='Description', help='Description of the medication time')


class MedicamentDosage(models.Model):
    _inherit = 'medicament.dosage'

    acs_medication_time_ids = fields.Many2many('acs.medication.time', 'acs_medication_time_dosage_rel', 'dosage_id', 'time_id', string='Medication Times',
        help='Medication times for this dosage. For example, 8:00 AM, 12:00 PM, etc.')


class AcsPatientMedication(models.Model):
    _name = 'acs.patient.medication'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Patient Medication"

    @api.depends('date')
    def acs_get_time(self):
        tz = timezone(self.env.user.tz)
        for rec in self:
            acs_time = ''
            if rec.id and rec.date:
                acs_time = pytz.UTC.localize(rec.date.replace(tzinfo=None), is_dst=False).astimezone(tz).strftime("%H:%M")
            rec.acs_time = acs_time
    
    @api.depends('done_date', 'date')
    def acs_get_given_status(self):
        for rec in self:
            given_state = False
            if rec.done_date and rec.date:
                tolerance_time = timedelta(minutes=15)  # 0.25 hours = 15 minutes
                lower_bound = rec.date - tolerance_time
                upper_bound = rec.date + tolerance_time
                if lower_bound <= rec.done_date <= upper_bound:
                    given_state = 'ontime'
                elif rec.done_date < lower_bound:
                    given_state = 'early'
                elif rec.done_date > upper_bound:
                    given_state = 'late'
            rec.given_state = given_state

    name = fields.Char(string='Name', readonly=True, default='New')
    nurse_id = fields.Many2one('hr.employee', string='Nurse', tracking=1)
    physician_id = fields.Many2one('hms.physician', string='Physician')
    hospitalization_id = fields.Many2one('acs.hospitalization', string='Hospitalization', tracking=1)
    patient_id = fields.Many2one('hms.patient', string='Patient', related='hospitalization_id.patient_id', store=True)
    date = fields.Datetime('Planned Date', required=True, tracking=1)
    done_date = fields.Datetime('Done Date', tracking=1)
    state = fields.Selection([
        ('draft', 'To-Do'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], default='draft', string='Status', tracking=1)
    given_state = fields.Selection([
        ('early', 'Early'),
        ('ontime', 'On Time'),
        ('late', 'Late')], compute="acs_get_given_status", string='Given Status', tracking=1, store=True)
    product_id = fields.Many2one('product.product', string='Medication', required=True, tracking=1)
    dose = fields.Float('Dosage', help="Amount of medication (eg, 250 mg) per dose", default=1.0)
    allowed_uom_ids = fields.Many2many('uom.uom', compute='_compute_allowed_uom_ids')
    dosage_uom_id = fields.Many2one('uom.uom', string='Unit of Dosage', help='Amount of Medicine (eg, mg) per dose', domain="[('id', 'in', allowed_uom_ids)]")
    form_id = fields.Many2one('drug.form',related='product_id.form_id', string='Form',help='Drug form, such as tablet or gel')
    route_id = fields.Many2one('drug.route', ondelete="cascade", string='Route', help='Drug form, such as tablet or gel')
    short_comment = fields.Char(string='Comment', help='Short comment on the specific drug')
    company_id = fields.Many2one('res.company', ondelete='restrict',
        string='Hospital', default=lambda self: self.env.company)
    notes = fields.Text(string='Note', help='Additional information about the medication')
    prescription_id = fields.Many2one('prescription.order', string='Prescription', help="Prescription this medication belongs to")
    acs_time = fields.Char(string='Time', compute="acs_get_time", store=True, index=True)

    @api.depends('product_id', 'product_id.uom_id', 'product_id.uom_ids')
    def _compute_allowed_uom_ids(self):
        for line in self:
            line.allowed_uom_ids = line.product_id.uom_id | line.product_id.uom_ids

    @api.model
    def default_get(self, fields):
        res = super(AcsPatientMedication, self).default_get(fields)
        if self.env.context.get('default_hospitalization_id'):
            res['hospitalization_id'] = self.env.context.get('default_hospitalization_id')
        return res
    
    @api.depends('patient_id.name')
    def _compute_display_name(self):
        for rec in self:
            if rec.state == 'draft':
                name = '⏳ '
            elif rec.state == 'done':
                name = '✅ '
            elif rec.state == 'cancel':
                name = '❌ '
            if rec.product_id:
                name += rec.product_id.name + ' [' + str(rec.dose) + ' ' + (rec.dosage_uom_id.name or '') + '] ' + rec.patient_id.name
            rec.display_name = name

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.form_id = self.product_id.form_id and self.product_id.form_id.id or False
            self.route_id = self.product_id.route_id and self.product_id.route_id.id or False
            self.dosage_uom_id = self.product_id.dosage_uom_id and self.product_id.dosage_uom_id.id or self.product_id.uom_id.id
            self.dose = self.product_id.dosage or 1
            self.short_comment = self.product_id.short_comment

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                seq_date = None
                if vals.get('date'):
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date']))
                vals['name'] = self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code('acs.patient.medication', sequence_date=seq_date) or _("New")
        return super().create(vals_list)

    def action_done(self):
        employee_id = self.env.user.employee_id
        if not self.nurse_id and employee_id and employee_id.department_id and employee_id.department_id.department_type == 'nurse':
            self.nurse_id = self.env.user.employee_id.id

        if not self.physician_id or not self.nurse_id:
            raise UserError(_("You must select a physician/nurse for this medication first."))
        self.state = "done"
        self.done_date = fields.Datetime.now()
    
    def action_cancel(self):
        self.state = "cancel"
    
    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_or_cancel(self):
        for record in self:
            if record.state not in ('draft', 'cancel'):
                raise UserError(_("You can delete a record in draft or cancelled state only."))
