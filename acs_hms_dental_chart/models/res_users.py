# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

DENTAL_CHART_FIELDS = ['acs_dental_color']

class ResUsers(models.Model):
    _inherit = "res.users"

    acs_dental_color = fields.Char(string='HMS Dental Chart Color', default="#985184")

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + DENTAL_CHART_FIELDS

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + DENTAL_CHART_FIELDS