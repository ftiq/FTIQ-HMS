# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
import base64
from odoo import fields, models, api, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager

class PhysicianController(http.Controller):

    @http.route(['/physicians', '/physicians/page/<int:page>'], type='http', auth='public', website=True)
    def acs_physician_page(self, page=1, search='', **kwargs):
        step = 8
        acs_selected_specialty_ids = request.httprequest.args.getlist('specialty_id')
        acs_selected_specialty_ids = [int(sid) for sid in acs_selected_specialty_ids if sid.isdigit()]
        domain = []
        if request.env.user._is_public():
            domain = [('website_published', '=', True)]
        if search:
            domain.append(('name', 'ilike', search))
        if acs_selected_specialty_ids:
            domain.append(('specialty_id', 'in', acs_selected_specialty_ids))

        total_physicians = request.env['hms.physician'].sudo().search_count(domain)
        physicians = request.env['hms.physician'].sudo().search(domain, limit=step, offset=(page - 1) * step)

        specialties = request.env['physician.specialty'].sudo().search([])

        pager = portal_pager(
            url="/physicians",
            url_args={'search': search},
            total=total_physicians,
            page=page,
            step=step
        )

        return request.render('acs_hms_website.acs_physician_page_template', {
            'pager': pager,
            'physicians': physicians,
            'specialties': specialties,
            'search': search,
            'acs_selected_specialty_ids': acs_selected_specialty_ids,
            'search_count': total_physicians,
        })

    @http.route('/physician/<string:physician>', type='http', auth='public', website=True)
    def acs_physician_detail(self, physician, **kwargs):
        physician = request.env['ir.http']._unslug(physician)
        physician = request.env['hms.physician'].sudo().search([('id', '=', physician[1])])
        if request.env.user._is_public() and not physician.website_published:
            return request.redirect('/web/login?redirect=/physician/%s' % physician.id)
        treatment = request.env['hms.treatment'].sudo().search([('physician_id','=',physician.id)])
        total_treatment = len(treatment)
        completed_treatment = len(treatment.filtered(lambda rec : rec.state=='done'))
        treatments_data = {
            'total_treatment':total_treatment,
            'completed_treatment':completed_treatment,
            'treatment_per':(completed_treatment/total_treatment*100)if total_treatment > 0 else 0,
        }
        return request.render('acs_hms_website.acs_physician_detail_template', {
            'physician': physician,
            'main_object': physician,
            'treatments_data': treatments_data,
        })
