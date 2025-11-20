# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from collections import defaultdict

class AccountMove(models.Model):
    _inherit = 'account.move'

    acs_invoice_summary_id = fields.Many2one('acs.invoice.summary', string='Invoice Summary')
    acs_categ_total = fields.Monetary(string='Category Total', readonly=True, currency_field='currency_id')

    def action_print_customer_invoice(self):
        category_dict = defaultdict(float)
        invoice_lines = self.invoice_line_ids

        for line in invoice_lines:
            if line.display_type == 'product' and line.product_id:
                product_category = line.product_id.categ_id.display_name
                category_dict[product_category] += line.price_total

        product_category_list = [{
            'product_category': category,
            'acs_categ_total': total,
        }
            for category, total in category_dict.items()
        ]
        return product_category_list


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    acs_invoice_summary_id = fields.Many2one('acs.invoice.summary', string='Invoice Summary')
    acs_product_category_id = fields.Many2one('product.category', related="product_id.categ_id", store=True, string='ACS Product Category')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    acs_invoice_summary_id = fields.Many2one('acs.invoice.summary', string='Invoice Summary')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: