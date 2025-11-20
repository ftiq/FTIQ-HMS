# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from werkzeug import urls

from odoo import api, fields, models, _


class PaymentLinkWizard(models.TransientModel):
    _inherit = 'payment.link.wizard'

    def _prepare_query_params(self, *args):
        """ Override of `payment` to add `acs_radiology_request_id` to the query params. """
        res = super()._prepare_query_params(*args)
        if self.res_model == 'acs.radiology.request':
            res.update({
                'acs_radiology_request_id': self.res_id,
            })
        return res
