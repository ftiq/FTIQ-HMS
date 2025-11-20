# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError, UserError


class AcsSubscription(models.Model):
    _name = 'acs.subscription'
    _inherit = ['acs.subscription','mail.thread', 'mail.activity.mixin', 'acs.hms.mixin']

    patient_id = fields.Many2one('hms.patient', string='Patient', ondelete="cascade", required=True)
    subscription_product_id = fields.Many2one('product.product', string='Subscription Service', related='contract_id.subscription_product_id', store=True)

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.partner_id = self.patient_id.partner_id

    #Replace module with core HMS module flow.
    def action_invoice_create(self):
        product_id = self.product_id
        if not product_id:
            raise UserError(_("Please Set proper contract first."))
        product_data = [{
            'product_id': product_id,
            'name': product_id.name + '\n' + 'Subscription No: ' + self.number,
            'price_unit': self.contract_id.price,
        }]
        inv_data = {}
        invoice = self.acs_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        invoice.subscription_id = self.id

class AcsContract(models.Model):
    _inherit = 'acs.contract'

    subscription_product_id = fields.Many2one('product.product', string='Subscription Service', ondelete="restrict", store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: