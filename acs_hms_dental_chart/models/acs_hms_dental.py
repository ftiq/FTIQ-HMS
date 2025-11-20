# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models ,_
from odoo.exceptions import UserError


class AcsHmsTooth(models.Model):
    _inherit="acs.hms.tooth"

    image = fields.Binary(string="Image")
    age_group = fields.Selection([
        ("child", "Child"),
        ("teen", "Teenager"),
        ("adult", "Adult"),
    ], string="Age Group", required=True, default="adult")

    is_child_tooth = fields.Boolean(string="Child", default=True)
    is_teen_tooth = fields.Boolean(string="Teenager", default=True)
    is_adult_tooth = fields.Boolean(string="Adult", default=True)

    @api.model
    def acs_get_age_group(self):
        data = {
            'child': 'Child',
            'teen': 'Teenager',
            'adult': 'Adult'
        }
        return dict(data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:   