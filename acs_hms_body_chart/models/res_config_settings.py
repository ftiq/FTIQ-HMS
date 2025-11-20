# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models,_


class ResCompany(models.Model):
    _inherit = 'res.company'

    acs_default_chart_image = fields.Binary('Default Chart Image', help="Image to use in chart by default.")
    acs_default_chart_image_name = fields.Char('Default Chart Image name')
    acs_default_male_chart_image = fields.Binary('Default Male Chart Image', help="Image to use in chart by default.")
    acs_default_male_chart_image_name = fields.Char('Default Male Chart Image name')
    acs_default_female_chart_image = fields.Binary('Default Female Chart Image', help="Image to use in chart by default.")
    acs_default_female_chart_image_name = fields.Char('Default Female Chart Image name')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    acs_default_chart_image = fields.Binary(related='company_id.acs_default_chart_image',
        string='Default Chart Image', readonly=False)
    acs_default_chart_image_name = fields.Char(related='company_id.acs_default_chart_image_name',
        string='Default Chart Image name', readonly=False)
    acs_default_male_chart_image = fields.Binary(related='company_id.acs_default_male_chart_image',
        string='Default Male Chart Image', readonly=False)
    acs_default_male_chart_image_name = fields.Char(related='company_id.acs_default_male_chart_image_name',
        string='Default male Chart Image name', readonly=False)
    acs_default_female_chart_image = fields.Binary(related='company_id.acs_default_female_chart_image',
        string='Default Female Chart Image', readonly=False)
    acs_default_female_chart_image_name = fields.Char(related='company_id.acs_default_female_chart_image_name',
        string='Default Female Chart Image name', readonly=False)