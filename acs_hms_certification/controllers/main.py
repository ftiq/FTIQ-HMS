1# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID

class ACSHms(http.Controller):

    @http.route(['/validate/certificatemanagement/<certificate_unique_code>'], type='http', auth="public", website=True, sitemap=False)
    def certificate_details(self, certificate_unique_code, **post):
        if certificate_unique_code:
            certificate = request.env['certificate.management'].sudo().search([('unique_code','=',certificate_unique_code)], limit=1)
            if certificate:
                return request.render("acs_hms_certification.acs_certificate_details", {'certificate': certificate})
        return request.render("acs_hms.acs_no_details")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
