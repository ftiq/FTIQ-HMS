# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

class AcsHms(http.Controller):

    @http.route(['/acs/data'], type='jsonrpc', auth="public", methods=['POST'], website=True)
    def acs_system_data(self, **kw):
        return request.env['res.company'].acs_get_blocking_data()


class HMSPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        values.update({
            'patient_id': request.env.user.acs_patient_id,
        })
        return values

    @http.route(['/my/family/new'], type='http', auth="user", website=True, sitemap=False)
    def family_member_new_form(self, redirect=None, **kw):
        values = self.get_default_form_data()
        values.update({'relation_id': 0, 'redirect': redirect})
        return request.render("acs_hms_base.create_family_member", values)

    @http.route('/acs/hms/family/create', type="http", auth="user", website=True, csrf=True, sitemap=False)
    def create_family_member(self, **kwargs):
        data = self.get_values_from_form(kwargs)
        new_patient = request.env['hms.patient'].sudo().create(data)
        request.env['acs.family.member'].sudo().create({
            'patient_id': request.env.user.acs_patient_id.id,
            'related_patient_id': new_patient.id,
            'relation_id': int(kwargs.get('relation_id')),
        })
        if kwargs.get('redirect'):
            return request.redirect(kwargs.get('redirect'))
        return request.redirect('/my')

    @http.route(['/my/family/update/<int:family_member_id>'], type='http', auth="user", website=True, sitemap=False)
    def family_member_update_form(self, family_member_id, redirect=None, **kw):
        values = self.get_default_form_data()
        family_member = request.env['acs.family.member'].sudo().search([('id','=',family_member_id)])
        patient_id = family_member.related_patient_id
        values.update({
            'record': patient_id,
            'relation_id': family_member.relation_id and family_member.relation_id.id or 0,
            'family_member': family_member.id,
            'redirect': redirect,
        })
        return request.render("acs_hms_base.update_family_member", values)

    @http.route('/acs/hms/family/update', type="http", auth="user", website=True, csrf=True, sitemap=False)
    def update_family_member(self, **kwargs):
        patient = request.env['hms.patient'].sudo().search([('id','=',kwargs.get('patient_id'))])
        data = self.get_values_from_form(kwargs)
        patient.write(data)
        family_member = request.env['acs.family.member'].sudo().search([('id','=',kwargs.get('family_member'))])
        if family_member:
            family_member.relation_id = int(kwargs.get('relation_id'))
        if kwargs.get('redirect'):
            return request.redirect(kwargs.get('redirect'))
        return request.redirect('/my')
    
    def get_default_form_data(self):
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        relations = request.env['acs.family.relation'].sudo().search([])
        patient_id = request.env['hms.patient'].sudo()
        return {
            'countries': countries, 
            'states': states, 
            'relations': relations, 
            'error': {},
            'record': patient_id,
        }
    
    def get_values_from_form(self, kwargs):
        data = {
            'name': kwargs.get('name'),
            'email': kwargs.get('email'),
            'phone': kwargs.get('phone'),
            'street': kwargs.get('street'),
            'city': kwargs.get('city'),
            'zip': kwargs.get('zip'),
            'gov_code': kwargs.get('gov_code'),
            'state_id': kwargs.get('state_id') and int(kwargs.get('state_id')) or False,
            'country_id': kwargs.get('country_id') and int(kwargs.get('country_id')) or False,
            'gender': kwargs.get('gender')
        }
        if kwargs.get('birthday'):
            data['birthday'] = kwargs.get('birthday')
        return data
