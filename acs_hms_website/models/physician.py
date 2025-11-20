# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
import base64
from odoo import fields, models, api, http, _
from odoo.http import request
from odoo.tools.translate import html_translate


class HmsPhysician(models.Model):
    _name = 'hms.physician'
    _inherit = ['hms.physician', 'website.seo.metadata','website.published.multi.mixin', 'website.searchable.mixin']

    acs_website_description = fields.Html(
        string="Physician Description",
        translate=html_translate,
        sanitize_overridable=True,
        sanitize_attributes=False,
        sanitize_form=False,
    )
    acs_physician_experience = fields.Char('Physician Experience')
    acs_physician_availability = fields.Text('Physician Availability')

    def _compute_website_url(self):
        super()._compute_website_url()
        for record in self:
            if record.id:
                record.website_url = "/physician/%s" % (self.env['ir.http']._slug(record))
 
    #=== BUSINESS METHODS ===#
    @api.model
    def _search_get_detail(self, website, order, options):
        search_fields = ['name']
        fetch_fields = ['id', 'name', 'website_url']
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'website_url': {'name': 'website_url', 'type': 'text', 'truncate': False},
            'image_url': {'name': 'image_url', 'type': 'text', 'truncate': False},
        }
        return {
            'model': 'hms.physician',
            'base_domain': [website.website_domain()],
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-folder-o',
            'order': 'name desc, id desc' if 'name desc' in order else 'name asc, id desc',
        }

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        with_image = 'image_url' in mapping
        results_data = super()._search_render_results(fetch_fields, mapping, icon, limit)
        for record, data in zip(self, results_data):
            if with_image:
                data['image_url'] = '/web/image/hms.physician/%s/image_128' % data['id']
        return results_data