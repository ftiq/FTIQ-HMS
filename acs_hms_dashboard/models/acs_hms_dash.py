# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF, format_datetime as tool_format_datetime
from collections import defaultdict
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class AcsHmsDashboard(models.Model):
    _name = "acs.hms.dashboard"
    _description = "Almighty HMS DASHBOARD"

    @api.model
    def acs_get_user_role(self):
        acs_is_physician = True if self.env.user.physician_count > 0 else False
        data = { 'acs_is_physician':acs_is_physician}
        return data
    
    def acs_get_company_domain(self):
        company = self.env.companies.ids
        company_domain = []
        if company:
            company.append(False)
            company_domain = [('company_id', 'in', company)]
        return company_domain
    
    @api.model
    def acs_get_dashboard_data(self, domain=[], date_domain=[]):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain
        date_base_domain = date_domain + company_domain
        Patient =  self.env['hms.patient']

        # Total Patient
        total_patient = Patient.search_count(base_domain)

        # My Total Patients
        patient_domain = base_domain + ['|',('primary_physician_id.user_id','=',self.env.uid), ('assignee_ids','in',self.env.user.partner_id.id)]
        my_total_patients = Patient.search_count(patient_domain)

        # Total Physician
        Physician = self.env['hms.physician']
        total_physician = Physician.search_count(base_domain)

        # Total Referring Physician
        Partner = self.env['res.partner']
        is_referring_physician_domain = base_domain + [('is_referring_doctor','=', True)]
        total_referring_physician = Partner.search_count(is_referring_physician_domain)

        # Total Procedures
        total_procedures = self.env['acs.patient.procedure'].search_count(date_base_domain)

        # Total Evaluations
        total_evaluations = self.env['acs.patient.evaluation'].search_count(date_base_domain)

        data = {
            "total_patient": total_patient,
            "my_total_patients": my_total_patients,
            "total_physician": total_physician,
            "total_referring_physician": total_referring_physician,
            "total_procedures": total_procedures,
            "total_evaluations": total_evaluations,
        }

        return data
    
    @api.model
    def acs_get_appointment_data(self, domain=[]):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        # Total Appointments
        Appointment = self.env['hms.appointment']
        total_appointments = Appointment.search_count(base_domain)

        # My Total Appointments
        my_total_appointment_domain = base_domain + [('physician_id.user_id','=',self.env.uid)]
        my_total_appointments =  Appointment.search_count(my_total_appointment_domain)

        data = {
            "total_appointments": total_appointments,
            "my_total_appointments": my_total_appointments,
        }
        return data
    
    @api.model
    def acs_get_treatment_data(self, domain=[]):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        # Total Treatments
        Treatment = self.env['hms.treatment']
        treatment_domain = company_domain + domain
        total_treatments = Treatment.search_count(treatment_domain)

        running_treatment_domain = treatment_domain + [('state','=','running')]
        total_running_treatments = Treatment.search_count(running_treatment_domain)

        my_treatment_domain = treatment_domain + [('physician_id.user_id','=',self.env.uid)]
        my_total_treatments = Treatment.search_count(my_treatment_domain)

        my_running_treatment_domain = treatment_domain + [('state','=','running'), ('physician_id.user_id','=',self.env.uid)]
        my_total_running_treatments = Treatment.search_count(my_running_treatment_domain)

        data = {
            "total_treatments": total_treatments,
            "total_running_treatments": total_running_treatments,
            "my_total_treatments": my_total_treatments,
            "my_total_running_treatments": my_total_running_treatments,
        }
        return data

    @api.model
    def acs_get_invoice_data(self, domain=[]):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        Invoice = self.env['account.move']
        open_invoice_domain = company_domain + domain
        open_invoice_domain += [('move_type','=','out_invoice'),('state','=','posted')]
        open_invoice = Invoice.search(open_invoice_domain)
        total_open_invoice = len(open_invoice)

        total_amount = 0
        for inv in open_invoice:
            total_amount += inv.amount_residual
        total_open_invoice_amount = round(total_amount, 2)

        currency = self.env.company.currency_id
        formatted_total_open_invoice_amount = formatLang(
            self.env, total_open_invoice_amount, currency_obj=currency
        )

        data = {
            "total_open_invoice": total_open_invoice,
            "formatted_total_open_invoice_amount": formatted_total_open_invoice_amount,
        }
        return data
    
    @api.model
    def acs_get_birthday_data(self, domain=[]):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')

        Patient = self.env['hms.patient']
        patient_birthday_domain = company_domain + [('birthday', 'like', today_month_day)]
        count_patients_birthday = Patient.search_count(patient_birthday_domain)

        employee_birthday_domain = company_domain + [('birthday', 'like', today_month_day)]
        Employee = self.env['hr.employee']
        count_employees_birthday = Employee.search_count(employee_birthday_domain)

        data = {
            "count_patients_birthday": count_patients_birthday,
            "count_employees_birthday": count_employees_birthday
        }
        return data
    
    @api.model
    def acs_get_appointment_table_data(self, domain=[], offset=0, limit=20):
        if domain is None:
            domain = []
        company_domain = self.acs_get_company_domain() or []
        base_domain = domain + company_domain

        user_role = self.acs_get_user_role()
        is_physician = user_role.get('acs_is_physician', False)
        Appointment = self.env['hms.appointment']
        appointment_domain = company_domain + domain

        appointment_data = []
        if is_physician:
            appointment_list = Appointment.search(appointment_domain + [('physician_id.user_id', '=', self.env.uid)], offset=offset, limit=limit)
        else:
            appointment_list = Appointment.search(appointment_domain, offset=offset, limit=limit)

        for appointment in appointment_list:
            appointment = appointment.sudo()
            app_date = tool_format_datetime(self.env, appointment.date, dt_format=False)
            appointment_data.append({
                'id': appointment.id,
                'name': appointment.name,
                'patient': appointment.patient_id.name,
                'image': appointment.patient_id.image_1920,
                'date': app_date or '',
                'physician': appointment.physician_id.name,
                'purpose': appointment.purpose_id.name or '',
                'planned_duration': '{0:02.0f}:{1:02.0f}'.format(*divmod(appointment.planned_duration * 60, 60)),
                'waiting_duration': '{0:02.0f}:{1:02.0f}'.format(*divmod(appointment.waiting_duration * 60, 60)),
                'appointment_duration': '{0:02.0f}:{1:02.0f}'.format(*divmod(appointment.appointment_duration * 60, 60)),
                'state': dict(appointment._fields['state']._description_selection(self.env)).get(appointment.state),
            })

        data = {
            "appointment_data": appointment_data,
            "total_count": Appointment.search_count(appointment_domain)
        }
        return data
    
    @api.model
    def acs_check_hms_receptionist_grp(self):
        return self.env.user.has_group('acs_hms.group_hms_receptionist')
    
    @api.model
    def acs_check_hms_js_doctor_grp(self):
        return self.env.user.has_group('acs_hms.group_hms_jr_doctor')
    
    @api.model
    def acs_check_hms_nurse_grp(self):
        return self.env.user.has_group('acs_hms.group_hms_nurse')
        
    @api.model
    def acs_check_hms_manager_grp(self):
        return self.env.user.has_group('acs_hms_base.group_hms_manager')
    
    @api.model
    def acs_check_account_invoice_grp(self):
        return self.env.user.has_group('account.group_account_invoice')

    @api.model
    def acs_get_kpi_full_data(self, domain=None, date_domain=None, invoice_domain=None):
        if domain is None:
            domain = []
        if date_domain is None:
            date_domain = []
        if invoice_domain is None:
            invoice_domain = []

        return {
            'dashboard': self.acs_get_dashboard_data(domain, date_domain),
            'appointments': self.acs_get_appointment_data(date_domain),
            'treatments': self.acs_get_treatment_data(date_domain),
            'invoices': self.acs_get_invoice_data(invoice_domain),
            'birthdays': self.acs_get_birthday_data(domain),
        }
    
    @api.model
    def acs_get_group_full_data(self):
        user = self.env.user
        return {
            "isPhysicianUser": self.acs_get_user_role(),
            "isHmsReceptionistGrp": self.acs_check_hms_receptionist_grp(),
            "isHmsNurseGrp": self.acs_check_hms_nurse_grp(),
            "isHmsJrDoctorGrp": self.acs_check_hms_js_doctor_grp(),
            "isHmsManagerGrp": self.acs_check_hms_manager_grp(),
            "isAccountInvoiceGrp": self.acs_check_account_invoice_grp(),
        }