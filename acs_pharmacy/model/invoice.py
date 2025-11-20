# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError, RedirectWarning
from datetime import timedelta


class AccountMove(models.Model): 
    _inherit = "account.move"

    patient_id = fields.Many2one('hms.patient',string="Patient")
    hospital_invoice_type = fields.Selection(selection_add=[('pharmacy', 'Pharmacy')])

    def get_scan_line_data(self, product, lot=False):
        res = super(AccountMove, self).get_scan_line_data(product, lot)
        res['acs_lot_id'] = lot and lot.id or False
        return res

    def acs_medicine_reminder_cron(self):
        today = fields.Datetime.now()
        seven_days_ago = today - timedelta(days=7)
        move_lines = self.env['account.move.line'].sudo().search([
            ('move_id.state','=', 'posted'),
            ('move_id.hospital_invoice_type','=', 'pharmacy'),
            ('product_id.acs_medicine_reminder','=',True),
            ('acs_reminder_sent_prescription', '=', False),
            ('acs_reminder_date', '>=', seven_days_ago),
            ('acs_reminder_date','<=', today)])
        moves = move_lines.mapped("move_id")
        for move in moves:
            line = move_lines.filtered(lambda l: l.move_id == move)
            med_name = ", ".join(line.mapped("product_id.name"))
            move.acs_send_reminder_msg(move, med_name, line)

    def acs_send_reminder_msg(self, move, med_name, line):
        template = self.env.ref("acs_pharmacy.acs_pharmacy_reminder_mail_template", raise_if_not_found=False)
        if template and move.partner_id.email:
            template.with_context(med_name=med_name).send_mail(move.id, raise_exception=False)
            line.acs_reminder_sent_prescription = True
        return move, med_name, line


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    acs_reminder_date = fields.Date(string="Reminder Date", compute="acs_compute_reminder_dates", copy=False, store=True)
    acs_reminder_sent_prescription = fields.Boolean(string="Reminder Sent", default=False)

    def acs_get_reminder_days(self, line):
        # Calculate reminder days based on half the quantity
        days = int(line.quantity / 2)
        return days

    @api.depends('quantity', 'product_id.common_dosage_id.qty_per_day', 'move_id.invoice_date')
    def acs_compute_reminder_dates(self):
        for line in self:
            if line.move_id.invoice_date and line.quantity > 0 and line.product_id.acs_medicine_reminder and line.product_id.common_dosage_id.qty_per_day > 0:
                reminder_days = self.acs_get_reminder_days(line)
                line.acs_reminder_date = (line.move_id.invoice_date) + timedelta(days=reminder_days)

    @api.onchange('quantity', 'acs_lot_id')
    def onchange_batch(self):
        res = super(AccountMoveLine, self).onchange_batch()
        if self.acs_lot_id and self.acs_lot_id.mrp:
            self.price_unit = self.acs_lot_id.mrp
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: