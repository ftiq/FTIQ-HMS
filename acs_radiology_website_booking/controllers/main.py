# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.acs_website_booking.controllers.main import AcsWebsite
from odoo.exceptions import AccessError, MissingError
from odoo import fields, http, tools, _, SUPERUSER_ID
from datetime import timedelta


class AcsWebsiteBooking(AcsWebsite):

    def acs_radiology_website_data(self, redirect=None, **post):
        company_id = request.env.user.sudo().company_id
        radiology_request = self.acs_user_website_booking_data(model='acs.radiology.request')
        values = {
            'payment_step': company_id.acs_allowed_booking_payment,
            'radiology_request': radiology_request,
            'redirect': redirect,
            'error_message': post.get('error_message'),
            'patient': request.env.user.acs_patient_id,
            'error': {}
        }
        return values
 
    @http.route(['/create/radiology/appointment'], type='http', auth='public', website=True, sitemap=True)
    def create_radiology_appointment(self, redirect=None, **post):
        values = self.acs_radiology_website_data(redirect, **post)
        values['locations'] = request.env['acs.radiology.room'].sudo().search([('allowed_online_booking','=',True)])
        return request.render("acs_radiology_website_booking.radiology_appointment_patient_and_location", values)

    @http.route(['/acs/radiology/slot'], type='http', auth='public', website=True, sitemap=False)
    def select_radiology_slot(self, redirect=None, **post):
        values = self.acs_radiology_website_data(redirect, **post)
        radiology_request = values.get('radiology_request')
        if not radiology_request:
            return request.redirect('/create/radiology/appointment')
        data = {}
        if post.get('radiology_room_id'):
            data['radiology_room_id'] = int(post.get('radiology_room_id'))
        else:
            error_message = _("Please Select Radiology Room to proceed ahead.")
            return request.redirect('/create/radiology/appointment?error_message=%s' % (error_message))

        if data:
            radiology_request.sudo().write(data)
 
        schedule_data = {'schedule_type': 'radiology', 'radiology_room_id': radiology_request.radiology_room_id.id}
        values['slots_data'] = request.env['acs.schedule'].acs_get_slot_data(**schedule_data)
        values['disable_dates'] = request.env['acs.schedule'].acs_get_disabled_dates(**schedule_data)
        values['last_date'] = fields.Date.today() + timedelta(days=request.env.user.sudo().company_id.acs_allowed_booking_online_days)
        return request.render("acs_radiology_website_booking.radiology_appointment_slot", values)

    @http.route(['/acs/radiology/tests'], type='http', auth='public', website=True, sitemap=False)
    def select_radiology_tests(self, redirect=None, **post):
        values = self.acs_radiology_website_data(redirect, **post)
        request.website.acs_get_request(model='acs.radiology.request')
        radiology_request = values.get('radiology_request')
        if not radiology_request or (radiology_request and not radiology_request.radiology_room_id):
            return request.redirect('/create/radiology/appointment')
        data = {}
        if post.get('schedule_slot_id'):
            data['schedule_slot_id'] = int(post.get('schedule_slot_id'))
        if data:
            radiology_request.sudo().write(data)
        if not radiology_request.schedule_slot_id:
            error_message = _("Please Select at least one Slot to proceed ahead.")
            return request.redirect('/acs/radiology/slot?error_message=%s' % (error_message))

        values['radiology_tests'] = request.env['acs.radiology.test'].sudo().search([
            ('radiology_room_ids','in',radiology_request.radiology_room_id.id),
            ('allowed_online_booking','=',True)])
        values['currency_id'] = request.env.user.sudo().company_id.currency_id
        return request.render("acs_radiology_website_booking.radiology_appointment_tests", values)

    @http.route(['/acs/radiology/patients'], type='http', auth='public', website=True, sitemap=False)
    def select_radiology_patients(self, redirect=None, **post):
        values = self.acs_radiology_website_data(redirect, **post)
        radiology_request = values.get('radiology_request')
        RequestLine = request.env['radiology.request.line']
        if not radiology_request or (radiology_request and not radiology_request.schedule_slot_id):
            return request.redirect('/create/radiology/appointment')

        if post.get('radiology_test_id'):
            radiology_request.sudo().line_ids.unlink()
            radiology_tests = request.env['acs.radiology.test'].sudo().search([('id','=',int(post.get('radiology_test_id')))])
            for test in radiology_tests:
                line = RequestLine.create({
                    'test_id': test.id,
                    'radiology_request_id': radiology_request.id,
                })
                line.sudo().onchange_test()

        if not radiology_request.line_ids:
            error_message = _("Please Select at least one Test to proceed ahead.")
            return request.redirect('/acs/radiology/tests?error_message=%s' % (error_message))

        values['family_members'] = request.env.user.acs_patient_id and request.env.user.acs_patient_id.family_member_ids or False
        return request.render("acs_radiology_website_booking.radiology_appointment_patients", values)

    @http.route(['/acs/radiology/request/confirm'], type='http', auth='public', website=True, sitemap=False)
    def acs_radiology_request_confirm(self, redirect=None, **post):
        values = self.acs_radiology_website_data(redirect, **post)
        radiology_request = values.get('radiology_request')
        company_id = request.env.user.sudo().company_id
        if not radiology_request or (radiology_request and len(radiology_request.line_ids)==0):
            return request.redirect('/create/radiology/appointment')

        if post.get('acs_patient_id'):
            radiology_request.sudo().write({'patient_id': int(post.get('acs_patient_id'))})
        else:
            error_message = _("Please Select at least one Patient to proceed ahead.")
            return request.redirect('/acs/radiology/patients?error_message=%s' % (error_message))

        data = self.acs_patient_radiology_req_data(**post)
        if data:
            radiology_request.sudo().write(data)
        radiology_request.sudo().button_requested()

        if company_id.acs_allowed_booking_payment:
            context = {'active_id': radiology_request.id, 'active_model': 'acs.radiology.request'}
            payment_link_wiz = request.env['payment.link.wizard'].sudo().with_context(context).create({})
            #if fee is 0 validate appointment
            if payment_link_wiz.amount==0:
                radiology_request.sudo().with_context(acs_online_transaction=True).button_accept()
                return request.render("acs_radiology_website_booking.radiology_req_thank_you", {'radiology_request': radiology_request})

            return request.redirect(payment_link_wiz.link)
        return request.render("acs_radiology_website_booking.radiology_req_thank_you", {'radiology_request': radiology_request})

    def acs_patient_radiology_req_data(self, **post):
        data = {}
        if post.get('notes'):
            data['notes'] = post.get('notes')
        return data

class AcsCustomerPortal(CustomerPortal):

    @http.route(['/my/radiology_requests/<model("acs.radiology.request"):request_id>/payment'], type='http', auth="user", website=True, sitemap=False)
    def radiology_request_payment(self, request_id, **kwargs):
        context = {'active_id': request_id.id, 'active_model': 'acs.radiology.request'}
        payment_link_wiz = request.env['payment.link.wizard'].sudo().with_context(context).create({})
        #if fee is 0 validate appointment
        if payment_link_wiz.amount==0:
            request_id.sudo().with_context(acs_online_transaction=True).button_accept()
            return request.render("acs_radiology_website_booking.radiology_req_thank_you", {'radiology_request': request_id})
        return request.redirect(payment_link_wiz.link)
    
    @http.route(['/my/radiology_requests/<int:request_id>/paid'], type='http', auth="public", website=True, sitemap=False)
    def my_radiology_request_paid(self, request_id=None, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('acs.radiology.request', request_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("acs_radiology.my_radiology_test_request", {'radiology_request': record_sudo, 'is_paid': True})


class AcsPaymentPortal(payment_portal.PaymentPortal):

    @http.route(['/my/radiology_requests/<model("acs.radiology.request"):request_id>/paymentprocess'], type='jsonrpc', auth="public", website=True, sitemap=False)
    def radiologyrequest_payment_process(self, request_id, access_token, **kwargs):
        logged_in = not request.env.user._is_public()
        partner_sudo = request.env.user.partner_id if logged_in else request_id.patient_id.partner_id
        self._validate_transaction_kwargs(kwargs)
        kwargs.update({ 
            'partner_id': partner_sudo.id,
            'currency_id': request_id.company_id.currency_id.id,
        })
        tx_sudo = self._create_transaction(
            custom_create_values={'acs_radiology_request_id': request_id.id}, **kwargs,
        )
        return tx_sudo._get_processing_values()

    def _get_extra_payment_form_values(self, **kwargs):
        """ Override of `payment` to reroute the payment flow to the portal view of the sales order.

        :param str sale_order_id: The sale order for which a payment is made, as a `sale.order` id.
        :return: The extended rendering context values.
        :rtype: dict
        """
        form_values = super()._get_extra_payment_form_values(**kwargs)
        acs_radiology_request_id = kwargs.get('acs_radiology_request_id')
        if acs_radiology_request_id:
            acs_radiology_request_id = self._cast_as_int(acs_radiology_request_id)
            order_sudo = request.env['acs.radiology.request'].sudo().browse(acs_radiology_request_id)

            # Interrupt the payment flow if the sales order has been canceled.
            if order_sudo.state == 'cancel':
                form_values['amount'] = 0.0

            # Reroute the next steps of the payment flow to the portal view of the sales order.
            form_values.update({
                'transaction_route': order_sudo.get_portal_url(suffix='/paymentprocess'),
                'landing_route': order_sudo.get_portal_url(suffix='/paid'),
                'access_token': order_sudo.access_token,
            })
        return form_values
