# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Physiotherapy(models.Model):
    _inherit = 'acs.physiotherapy'

    subscription_id = fields.Many2one("acs.subscription", "Subscription", ondelete="restrict")

    @api.onchange("subscription_id")
    def onchange_subscription_id(self):
        if self.subscription_id:
            if self.subscription_id.acs_type=='full':
                self.invoice_exempt = True
            else:
                self.pricelist_id = self.subscription_id.pricelist_id and self.subscription_id.pricelist_id.id or False

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            subscription = self.env['acs.subscription'].sudo().search([('state','=','active'),('res_model_id.model','=','acs.physiotherapy'),('patient_id','=',self.patient_id.id)], limit=1)
            self.subscription_id = subscription and subscription.id or False

    def action_done(self):
        res = super().action_done()
        if self.subscription_id and self.subscription_id.remaining_service<=0:
            self.subscription_id.action_done()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: