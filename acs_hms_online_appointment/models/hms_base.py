# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models,_,Command
from datetime import datetime
from datetime import timedelta


class Appointment(models.Model):
    _inherit = 'hms.appointment'

    schedule_date = fields.Date(string='Schedule Date')
    schedule_slot_id = fields.Many2one('acs.schedule.slot.lines', string='Schedule Slot')
    booked_online = fields.Boolean('Booked Online')

    def _get_and_set_external_taxes_on_eligible_records(self):
        # dummy method to prevent AttributeError
        return True

    @api.model
    def clear_appointment_cron(self):
        if self.env.company.hms_app_allowed_booking_payment:
            appointments = self.search([('booked_online','=', True),('state','=','draft')])
            for appointment in appointments:
                #cancel appointment after 20 minute if not paid
                create_time = appointment.create_date + timedelta(minutes=20)
                if create_time <= datetime.now():
                    if appointment.invoice_id:
                        if appointment.invoice_id.state=='paid':
                            continue
                        appointment.invoice_id.action_invoice_cancel()
                    appointment.appointment_cancel()

    @api.onchange('schedule_slot_id')
    def onchange_schedule_slot_id(self):
        if self.schedule_slot_id:
            self.date = self.schedule_slot_id.from_slot
            self.date_to = self.schedule_slot_id.to_slot

    @api.onchange('schedule_date')
    def onchange_schedule_date(self):
        if self.schedule_date and self.schedule_slot_id and self.schedule_date!=self.schedule_slot_id.acs_slot_id.slot_date:
            self.schedule_slot_id = False

    def _get_default_payment_link_values(self):
        self.ensure_one()
        product_data = self.acs_appointment_inv_product_data()
        amount = self.acs_get_total_amount(product_data, self.patient_id.partner_id)

        return {
            'amount': amount,
            'currency_id': self.company_id.currency_id.id,
            'partner_id': self.patient_id.partner_id.id,
            'amount_max': amount
        }

    def acs_get_total_amount(self, product_data, partner):
        total_amount = 0
        for data in product_data:
            product = data.get('product_id')
            if product:
                acs_pricelist_id = self.env.context.get('acs_pricelist_id')
                if not data.get('price_unit') and (partner.property_product_pricelist or acs_pricelist_id):
                    if acs_pricelist_id:
                        pricelist_id = self.env['product.pricelist'].browse(acs_pricelist_id)
                    else:
                        pricelist_id = partner.property_product_pricelist
                    price = pricelist_id._get_product_price(product, data.get('quantity',1.0))
                else:
                    price = data.get('price_unit', product.list_price)
                if product.taxes_id:
                    taxes = product.taxes_id.compute_all(price, product=product, partner=partner)
                    price = taxes['total_included']
                total_amount += price * data.get('quantity',1.0)
        return total_amount

    def appointment_confirm(self):
        res = super().appointment_confirm()
        if self.patient_id.email and not self.company_id.acs_auto_appo_confirmation_mail and not self.env.context.get('acs_online_transaction') and self.booked_online:
            template = self.env.ref('acs_hms.acs_appointment_email')
            template.sudo().send_mail(self.id, raise_exception=False)
        return res

class HrDepartment(models.Model):
    _inherit = "hr.department"

    allowed_online_booking = fields.Boolean("Allowed Online Booking", help="Publish on website")
    basic_info = fields.Char("Basic Info", help="Show basic information on website")
    image = fields.Binary(string='Image')
    allow_home_appointment = fields.Boolean("Allowed Home Visit Booking")
    show_fee_on_booking = fields.Boolean("Show Fees")


class HmsPhysician(models.Model):
    _inherit = "hms.physician"

    allowed_online_booking = fields.Boolean("Allowed Online Booking", help="Publish on website")
    basic_info = fields.Char("Basic Info", help="Show basic information on website")
    allow_home_appointment = fields.Boolean("Allowed Home Visit Booking")
    show_fee_on_booking = fields.Boolean("Show Fees")


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    acs_appointment_id = fields.Many2one("hms.appointment", string="Appointment")

    #Update Payments directs after successful payment.
    def _post_process(self):
        res = super()._post_process()        
        for tx in self.filtered(lambda t: t.operation != 'validation' and t.acs_appointment_id):
            tx._acs_update_appointment()
        return res

    #Update appointment data.
    def _acs_update_appointment(self):
        self.ensure_one()
        self.acs_appointment_id.sudo().with_context(acs_online_transaction=True,default_create_stock_moves=False).create_invoice()
        if self.acs_appointment_id.sudo().invoice_id.state=='draft':
            self.acs_appointment_id.sudo().invoice_id.action_post()
        if self.payment_id and self.acs_appointment_id.sudo().invoice_id:
            self.payment_id.invoice_ids |= self.acs_appointment_id.sudo().invoice_id
        if self.acs_appointment_id.sudo().state!='confirm':
            self.acs_appointment_id.sudo().with_context(acs_online_transaction=True).appointment_confirm()

        # Setup access token in advance to avoid serialization failure between
        # edi postprocessing of invoice and displaying the sale order on the portal
        self.acs_appointment_id.invoice_id._portal_ensure_token()
        self.invoice_ids = [Command.set( [self.acs_appointment_id.invoice_id.id])]

