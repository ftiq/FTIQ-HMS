# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.exceptions import AccessError, MissingError


class HMSPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        Appointment = request.env['hms.appointment']
        Prescription = request.env['prescription.order']
        Evaluation = request.env['acs.patient.evaluation']
        if 'appointment_count' in counters:
            values['appointment_count'] = Appointment.search_count([]) \
                if Appointment.has_access('read') else 0
        if 'prescription_count' in counters:
            values['prescription_count'] = Prescription.search_count([]) \
                if Prescription.has_access('read') else 0
        if 'evaluation_count' in counters:
            values['evaluation_count'] = Evaluation.search_count([]) \
                if Evaluation.has_access('read') else 0
        return values

    @http.route(['/my/appointments', '/my/appointments/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_appointments(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Appointment = request.env['hms.appointment']
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = Appointment.search_count([])
 
        pager = portal_pager(
            url="/my/appointments",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        partner = request.env.user.partner_id.commercial_partner_id
        appointments = Appointment.search([],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'appointments': appointments,
            'page_name': 'appointment',
            'default_url': '/my/appointments',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("acs_hms_portal.my_appointments", values)

    @http.route(['/my/appointments/<int:appointment_id>'], type='http', auth="public", website=True, sitemap=False)
    def my_appointments_appointment(self, appointment_id=None, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('hms.appointment', appointment_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        acs_message = kw.get('acs_message')
        return request.render("acs_hms_portal.my_appointments_appointment", {'appointment': record_sudo, 'acs_message': acs_message})

    @http.route(['/acs/cancel/appointment/<int:appointment_id>'], type='http', auth="public", website=True, sitemap=False)
    def acs_cancel_appointment(self, appointment_id, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('hms.appointment', appointment_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        record_sudo.write({
            'cancel_reason': kw.get('cancel_reason')
        })
        record_sudo.appointment_cancel()
        acs_message = _("Appointment is cancelled!")
        return request.render("acs_hms_portal.my_appointments_appointment", {'appointment': record_sudo, 'acs_message': acs_message})

    @http.route(['/acs/confirm/appointment/<int:appointment_id>'], type='http', auth="public", website=True, sitemap=False)
    def acs_confirm_appointment(self, appointment_id, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('hms.appointment', appointment_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        record_sudo.appointment_confirm()
        acs_message = _("Appointment is confirmed sucesfully!")
        return request.render("acs_hms_portal.my_appointments_appointment", {'appointment': record_sudo, 'acs_message': acs_message})

    #Prescriptions
    @http.route(['/my/prescriptions', '/my/prescriptions/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_prescriptions(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Prescription = request.env['prescription.order']
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = Prescription.search_count([])
 
        pager = portal_pager(
            url="/my/prescriptions",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        partner = request.env.user.partner_id.commercial_partner_id
        prescriptions = request.env['prescription.order'].search([],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'prescriptions': prescriptions,
            'page_name': 'prescription',
            'default_url': '/my/prescriptions',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("acs_hms_portal.my_prescriptions", values)

    @http.route(['/my/prescriptions/<int:prescription_id>'], type='http', auth="public", website=True, sitemap=False)
    def my_appointments_prescription(self, prescription_id=None, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('prescription.order', prescription_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("acs_hms_portal.my_prescriptions_prescription", {'prescription': record_sudo})

    def details_form_validate(self, data):
        error, error_message = super(HMSPortal, self).details_form_validate(data)
        # prevent VAT/name change if invoices | Prescription exist
        partner = request.env['res.users'].browse(request.uid).partner_id
        has_prescription = request.env['prescription.order'].search([], limit=1)
        if has_prescription:
            if 'name' in data and (data['name'] or False) != (partner.name or False):
                error['name'] = 'error'
                error_message.append(_('Changing your name is not allowed once Prescriptions have been issued for your account. Please contact us directly for this operation.'))
        return error, error_message

    #Evaluations
    @http.route(['/my/evaluations', '/my/evaluations/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_evaluations(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Evaluation = request.env['acs.patient.evaluation']
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = Evaluation.search_count([])
 
        pager = portal_pager(
            url="/my/evaluations",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        partner = request.env.user.partner_id.commercial_partner_id
        evaluations = Evaluation.search([],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'evaluations': evaluations,
            'page_name': 'evaluation',
            'default_url': '/my/evaluations',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("acs_hms_portal.my_evaluations", values)

    @http.route(['/my/evaluations/<int:evaluation_id>'], type='http', auth="public", website=True, sitemap=False)
    def my_evaluation(self, evaluation_id=None, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('acs.patient.evaluation', evaluation_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("acs_hms_portal.my_evaluation", {'evaluation': record_sudo})

    @http.route(['/my/evaluations/create'], type='http', auth="user", website=True, sitemap=False)
    def my_evaluation_create(self, **kw):
        partner = request.env.user.partner_id.commercial_partner_id
        patient_id = request.env['hms.patient'].sudo().search([('partner_id','=', partner.id)], limit=1)
        values = {
            'patient_id': patient_id,
        }
        return request.render("acs_hms_portal.create_evaluation", values)

    @http.route(['/my/evaluations/charts'], type='http', auth="user", website=True, sitemap=False)
    def my_evaluation_charts(self, **kw):
        partner = request.env.user.partner_id.commercial_partner_id
        patient_id = request.env['hms.patient'].sudo().search([('partner_id','=', partner.id)], limit=1)
        values = {
            'patient_id': patient_id,
        }
        return request.render("acs_hms_portal.my_evaluation_charts", values)

