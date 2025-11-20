# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command ,_
from odoo.exceptions import UserError
from collections import defaultdict
import time
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import format_datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF, format_datetime as tool_format_datetime

import logging
_logger = logging.getLogger(__name__)

class ACSPatient(models.Model):
    _inherit = 'hms.patient'

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        Prescription = self.env['prescription.order']
        for rec in self:
            rec.prescription_count = Prescription.search_count([('patient_id','=',rec.id)])
            rec.treatment_count = len(rec.treatment_ids)
            rec.appointment_count = len(rec.appointment_ids)
            rec.evaluation_count = len(rec.evaluation_ids)
            rec.patient_procedure_count = len(rec.patient_procedure_ids)

    def _acs_get_attachments(self):
        attachments = super(ACSPatient, self)._acs_get_attachments()
        attachments += self.appointment_ids.mapped('attachment_ids')
        return attachments

    @api.model
    def _get_service_id(self):
        registration_product = False
        if self.env.company.patient_registration_product_id:
            registration_product = self.env.company.patient_registration_product_id.id
        return registration_product

    @api.depends('evaluation_ids.state')
    def _get_last_evaluation(self):
        for rec in self:
            evaluation_ids = rec.evaluation_ids.filtered(lambda x: x.state=='done')
                   
            if evaluation_ids:
                rec.last_evaluation_id = evaluation_ids[0].id if evaluation_ids else False
            else:
                rec.last_evaluation_id = False

    def acs_check_cancellation_flag(self):
        acs_flag_days = self.env.user.sudo().company_id.acs_flag_days or 365
        acs_flag_count_limit = self.env.user.sudo().company_id.acs_flag_count_limit or 1
        date_start = fields.Datetime.now() - relativedelta(days=acs_flag_days)
        date_end = fields.Datetime.now()
        for rec in self:
            show_cancellation_warning_flag = False
            cancelled_appointments = self.env['hms.appointment'].sudo().search_count([
                ('date','>=', date_start), 
                ('date','<=', date_end),
                ('patient_id','=', rec.id),
                ('state', 'in', ['cancel'])
            ])
            if cancelled_appointments >= acs_flag_count_limit:
                show_cancellation_warning_flag = True
            rec.show_cancellation_warning_flag = show_cancellation_warning_flag
            rec.acs_flag_days = acs_flag_days
            rec.acs_cancelled_appointments = cancelled_appointments

    ref_doctor_ids = fields.Many2many('res.partner', 'rel_doc_pat', 'doc_id', 
        'patient_id', 'Referring Doctors', domain=[('is_referring_doctor','=',True)])

    #Diseases
    medical_history = fields.Text(string="Past Medical History")
    patient_diseases_ids = fields.One2many('hms.patient.disease', 'patient_id', string='Diseases')

    #Family Form Tab
    genetic_risks_ids = fields.One2many('hms.patient.genetic.risk', 'patient_id', 'Genetic Risks')
    family_history_ids = fields.One2many('hms.patient.family.diseases', 'patient_id', 'Family Diseases History')
    department_ids = fields.Many2many('hr.department', 'patint_department_rel','patient_id', 'department_id',
        domain=[('patient_department', '=', True)], string='Departments')

    medication_ids = fields.One2many('hms.patient.medication', 'patient_id', string='Medications')
    ethnic_group_id = fields.Many2one('acs.ethnicity', string='Ethnic group')
    cod_id = fields.Many2one('hms.diseases', string='Cause of Death')

    prescription_count = fields.Integer(compute='_rec_count', string='# Prescriptions')
    treatment_ids = fields.One2many('hms.treatment', 'patient_id', 'Treatments')
    treatment_count = fields.Integer(compute='_rec_count', string='# Treatments')
    appointment_count = fields.Integer(compute='_rec_count', string='# Appointments')
    appointment_ids = fields.One2many('hms.appointment', 'patient_id', 'Appointments')
    medical_alert_ids = fields.Many2many('acs.medical.alert', 'patient_medical_alert_rel','patient_id', 'alert_id',
        string='Medical Alerts')
    allergy_ids = fields.Many2many('acs.medical.allergy', 'patient_allergies_rel','patient_id', 'allergies_id',
        string='Allergies')
    registration_product_id = fields.Many2one('product.product', default=_get_service_id, string="Registration Service")
    invoice_id = fields.Many2one("account.move","Registration Invoice", copy=False)

    evaluation_count = fields.Integer(compute='_rec_count', string='# Evaluations')
    evaluation_ids = fields.One2many('acs.patient.evaluation', 'patient_id', 'Evaluations')

    last_evaluation_id = fields.Many2one("acs.patient.evaluation", string="Last Evaluation", compute=_get_last_evaluation, readonly=True, store=True)
    weight = fields.Float(related="last_evaluation_id.weight", string='Weight', help="Weight in KG", readonly=True)
    height = fields.Float(related="last_evaluation_id.height", string='Height', help="Height in cm", readonly=True)
    temp = fields.Float(related="last_evaluation_id.temp", string='Temp', readonly=True)
    hr = fields.Integer(related="last_evaluation_id.hr", string='HR', help="Heart Rate", readonly=True)
    rr = fields.Integer(related="last_evaluation_id.rr", string='RR', readonly=True, help='Respiratory Rate')
    systolic_bp = fields.Integer(related="last_evaluation_id.systolic_bp", string="Systolic BP")
    diastolic_bp = fields.Integer(related="last_evaluation_id.diastolic_bp", string="Diastolic BP")
    spo2 = fields.Integer(related="last_evaluation_id.spo2", string='SpO2', readonly=True, 
        help='Oxygen Saturation, percentage of oxygen bound to hemoglobin')
    rbs = fields.Integer(related="last_evaluation_id.rbs", string='RBS', readonly=True, 
        help='Random blood sugar measures blood glucose regardless of when you last ate.')
    bmi = fields.Float(related="last_evaluation_id.bmi", string='Body Mass Index', readonly=True)
    bmi_state = fields.Selection(related="last_evaluation_id.bmi_state", string='BMI State', readonly=True)

    pain_level = fields.Selection(related="last_evaluation_id.pain_level", string="Pain Level", readonly=True)
    pain = fields.Selection(related="last_evaluation_id.pain", string="Pain", readonly=True)
    
    acs_weight_name = fields.Char(related="last_evaluation_id.acs_weight_name", string='Patient Weight unit of measure label')
    acs_height_name = fields.Char(related="last_evaluation_id.acs_height_name", string='Patient Height unit of measure label')
    acs_temp_name = fields.Char(related="last_evaluation_id.acs_temp_name", string='Patient Temp unit of measure label')
    acs_spo2_name = fields.Char(related="last_evaluation_id.acs_spo2_name", string='Patient SpO2 unit of measure label')
    acs_rbs_name = fields.Char(related="last_evaluation_id.acs_rbs_name", string='Patient RBS unit of measure label')

    patient_procedure_ids = fields.One2many('acs.patient.procedure', 'patient_id', 'Patient Procedures')
    patient_procedure_count = fields.Integer(compute='_rec_count', string='# Patient Procedures')
    show_cancellation_warning_flag = fields.Boolean(compute='acs_check_cancellation_flag', string='Show Cancellation Flag')
    acs_flag_days = fields.Integer(compute='acs_check_cancellation_flag', string='Flag Days')
    acs_cancelled_appointments = fields.Integer(compute='acs_check_cancellation_flag', string='Cancelled Appointments')

    @api.model
    def acs_get_evaluation_color(self):
        return {"acs_evaluation_color": self.env.user.acs_evaluation_color or '#985184'}

    @api.model
    def acs_get_evolution_graph_data(self, patient, field_name, unit=None, domain=[], group_by="none"):
        Evaluation = self.env['acs.patient.evaluation']
        final_domain = [('patient_id','=', patient)] + domain
        _logger.info("\n\n final_domain ----- %s", final_domain)
        
        fields_to_read = ['date', field_name, 'patient_id']
        if unit and unit in Evaluation._fields:
            fields_to_read.append(unit)

        records = Evaluation.sudo().search_read(
            domain=final_domain,
            fields=fields_to_read,
            order="date asc"
        )
        _logger.info("\n\n records ----- %s", records)
        if not records:
            return {"labels": [], "data": [], "tooltiptext": []}

        if group_by == "none":
            return self._acs_get_none_grp_evaluation(records, field_name, unit)
        else:
            return self._acs_get_with_grp_evaluation(records, field_name, unit, group_by)
        
    def _acs_get_none_grp_evaluation(self, records, field_name, unit=None):
        labels, data, tooltiptext, full_dates, units = [], [], [], [], []
        field = self._fields.get(field_name)
        field_label = field.string if field else field_name.capitalize()
        is_field_unit = unit and unit in self._fields

        for rec in records:
            date = rec.get("date")
            value = rec.get(field_name)
            patient = rec.get("patient_id")  # (id, name)

            if date and value not in (False, None):
                date_obj = fields.Datetime.from_string(date)
                labels.append(date_obj.strftime("%Y-%m-%d"))

                user_tz = self.env.user.tz or 'UTC'
                local_dt = fields.Datetime.context_timestamp(self.with_context(tz=user_tz), date_obj)
                full_dates.append(local_dt.strftime("%Y-%m-%d %I:%M:%S %p"))

                data.append(float(value))

                if is_field_unit:
                    unit_val = rec.get(unit) or ""
                else:
                    unit_val = unit or ""
                units.append(unit_val.capitalize())

                tooltiptext.append(f"{patient[1] if patient else 'Unknown'} - {field_label}")

        return {
            "labels": labels,
            "data": data,
            "tooltiptext": tooltiptext,
            "full_dates": full_dates,
            "units": units,
            "field_label": field_label,   #field string
            "field_name": field_name,     #field technical name too
        }

    def _acs_get_with_grp_evaluation(self, records, field_name, group_by, unit=None):
        grouped_data = defaultdict(list)
        grouped_units = defaultdict(list)
        field = self._fields.get(field_name)
        field_label = field.string if field else field_name.capitalize()

        is_field_unit = unit and unit in self._fields

        for rec in records:
            date = rec.get("date")
            value = rec.get(field_name)

            if date and value not in (False, None):
                date_obj = fields.Datetime.from_string(date)

                if group_by == "day":
                    key = date_obj.strftime("%d %b %Y")
                elif group_by == "week":
                    key = f"Week {date_obj.strftime('%W, %Y')}"
                elif group_by == "month":
                    key = date_obj.strftime("%b %Y")
                elif group_by == "year":
                    key = date_obj.strftime("%Y")
                else:
                    key = date_obj.strftime("%Y-%m-%d")

                grouped_data[key].append(float(value))

                if is_field_unit:
                    unit_val = rec.get(unit) or ""
                else:
                    unit_val = unit or ""

                if isinstance(unit_val, str):
                    unit_val = unit_val.capitalize()

                grouped_units[key].append(unit_val)

        aggregated = {k: (sum(v) / len(v)) for k, v in grouped_data.items()}
        #MKA: pick the last non-empty unit for each group
        aggregated_units = {k: (u[-1] if u else "") for k, u in grouped_units.items()}

        sorted_data = sorted(aggregated.items(), key=lambda x: x[0])
        labels = [x[0] for x in sorted_data]
        data = [x[1] for x in sorted_data]
        units = [aggregated_units[x[0]] for x in sorted_data]

        return {
            "labels": labels,
            "data": data,
            "units": units,
            "field_label": field_label,
            "field_name": field_name,
        }

    def action_view_patient_procedures(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.action_acs_patient_procedure")
        action['domain'] = [('id', 'in', self.patient_procedure_ids.ids)]
        action['context'] = {'default_patient_id': self.id}
        return action

    def acs_show_evaluation_chart(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'AlmightyHmsEvaluation',
            'params': {
                'active_id': self.id,
                'active_model': 'hms.patient',
                'domain': [('id', '=', self.id)],
            }
        }

    def create_invoice(self):
        product_id = self.registration_product_id or self.env.company.patient_registration_product_id
        if not product_id:
            raise UserError(_("Please Configure Registration Product in Configuration first."))

        invoice = self.acs_create_invoice(partner=self.partner_id, patient=self, product_data=[{'product_id': product_id}], inv_data={'hospital_invoice_type': 'patient'})
        self.invoice_id = invoice.id

    def action_appointment(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.action_appointment")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_physician_id.id}
        return action

    def action_prescription(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.act_open_hms_prescription_order_view")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_physician_id.id}
        return action

    def action_treatment(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.acs_action_form_hospital_treatment")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_physician_id.id}
        return action

    def action_evaluation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.action_acs_patient_evaluation")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_physician_id.id}
        return action

    acs_patient_progress = fields.Float(string="Patient Profile Progress", compute="compute_patient_progress")
    show_patient_progress = fields.Boolean(string="Show Patient Progress", compute="compute_view_patient_progress")

    def compute_view_patient_progress(self):
        for rec in self:
            company = rec.company_id or self.env.company
            rec.show_patient_progress = company.sudo().acs_view_patient_progress

    def compute_patient_progress(self):
        for rec in self:
            company = rec.company_id or self.env.company
            acs_patient_progress = 0.0
            dynamic_fields = company.sudo().acs_patient_field_ids.filtered(lambda f: f.model == 'hms.patient').mapped('name')
            if dynamic_fields:
                total = len(dynamic_fields)
                filled = sum(1 for field_name in dynamic_fields if getattr(rec, field_name))
                acs_patient_progress = (filled / total * 100) if total else 0.0
            rec.acs_patient_progress = acs_patient_progress

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: