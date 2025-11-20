# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class AcsConsentFormTemplate(models.Model):
    _inherit = 'acs.consent.form.template'

    acs_is_hospitalization_template = fields.Boolean("Hospitalization Template", default=False)
    acs_is_surgery_template = fields.Boolean("Surgery Template", default=False)

class AcsConsentForm(models.Model):
    _inherit = 'acs.consent.form'

    hospitalization_id = fields.Many2one("acs.hospitalization",string="Hospitalization",ondelete="cascade",)
    surgery_id = fields.Many2one("hms.surgery",string="Surgery",ondelete="cascade",)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: