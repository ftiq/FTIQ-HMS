# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    acs_bill_sheet_ids = fields.One2many('acs.bill.sheet', 'partner_id', 'Bill Sheets')
    acs_bill_sheet_count = fields.Integer(compute='acs_rec_count', string='# Bill Sheets')

    def acs_rec_count(self):
        for rec in self:
            rec.acs_bill_sheet_count = self.env['acs.bill.sheet'].search_count([('partner_id', '=', rec.id)])

    def action_bill_sheet(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_bill_sheet.action_acs_bill_sheet")
        action['domain'] = [('id','=',self.id)]
        action['context'] = {}
        return action