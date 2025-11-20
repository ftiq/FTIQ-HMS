# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class AcsBillSheet(models.Model):
    _inherit = 'acs.bill.sheet'

    @api.depends('laboratory_request_ids','laboratory_request_ids.total_price')
    def _amount_all(self):
        vals = super()._amount_all()
        for record in self:
            amount_total = record.amount_total
            if record.bill_type == 'lab':
                for line in record.laboratory_request_ids:
                    amount_total += line.total_price
            record.amount_total = amount_total
        return vals
    
    def _acs_rec_count(self):
        res = super()._acs_rec_count()
        for rec in self:
            rec.laboratory_request_count = len(rec.laboratory_request_ids)
        return res

    bill_type = fields.Selection(selection_add=[('lab', 'Lab')])
    laboratory_request_ids = fields.One2many('acs.laboratory.request', 'bill_sheet_id', string='Lines')
    laboratory_request_count = fields.Integer(compute='_acs_rec_count', string='# laboratory Requests')

    def acs_get_data(self):
        vals = super().acs_get_data()
        if self.bill_type == 'lab':
            self.laboratory_request_ids.write({'bill_sheet_id': False})
            domain = [('bill_sheet_id','=',False),
                    ('laboratory_id.partner_id','=',self.partner_id.id),
                    ('date','>=',self.date_from),
                    ('date','<=',self.date_to)]
            laboratory_request_ids = self.env['acs.laboratory.request'].search(domain)
            laboratory_request_ids.write({'bill_sheet_id': self.id})
        return vals

    def acs_get_laboratory_bill_data(self,product_data=[]):
        laboratory_request_ids = self.laboratory_request_ids
        for line in laboratory_request_ids.mapped('line_ids'):
            product_id = line.test_id.product_id
            product_data.append({
                'name': '[' + line.request_id.name + '] ' + line.request_id.patient_id.name + ': ' + product_id.name,
                'product_id': product_id, 
                'quantity': line.quantity, 
                'price_unit': line.sale_price
            })
            if product_id.is_kit_product:
                for kit_line in product_id.acs_kit_line_ids:
                    product_data.append({
                        'name': '[' + line.request_id.name + '] ' + line.request_id.patient_id.name + ': ' + product_id.name,
                        'product_id': kit_line.product_id, 
                        'quantity': kit_line.product_qty * line.quantity,
                        'price_unit': kit_line.product_id.list_price
                    })
        return product_data
    
    def acs_get_bill_data(self):
        product_data = super().acs_get_bill_data()
        self.acs_get_laboratory_bill_data(product_data=product_data)
        return product_data

    def acs_create_bill(self):
        bill = super().acs_create_bill()
        for laboratory in self.laboratory_request_ids:
            laboratory.lab_bill_id = bill.id
        return bill

    def action_laboratory_requests(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_laboratory.hms_action_lab_test_request")
        action['domain'] = [('id','in',self.laboratory_request_ids.ids)]
        action['context'] = {}
        return action