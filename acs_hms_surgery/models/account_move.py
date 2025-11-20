# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models,_, Command
from odoo.exceptions import ValidationError, UserError
from odoo.fields import Command

class AccountMove(models.Model):
    _inherit = "account.move"

    surgery_id = fields.Many2one('hms.surgery', string='Surgery')
    hospital_invoice_type = fields.Selection(selection_add=[('surgery', 'Surgery')])

    @api.depends('acs_package_id.service_amount', 'acs_package_id.amount_total', 
                 'acs_package_id.package_type', 'acs_package_id.product_id')
    def acs_compute_package_amount(self):
        for move in self:
            total_amount = 0.0
            package = move.acs_package_id
            if package.package_type == 'dynamic':
                # MKA: If there is a dynamic package containing both a service product and a package product, both should be considered.
                if package.product_id and package.service_amount and package.order_line:
                    total_amount = package.service_amount + package.amount_total
                else:
                    total_amount = package.amount_total
            else:
                if package.service_amount:
                    total_amount = package.service_amount
                else:
                    total_amount = package.amount_total
            move.acs_package_total_amount = total_amount

    @api.depends('acs_package_invoice_line_ids.price_total')
    def acs_compute_used_amount(self):
        for move in self:
            used_amount = 0.0
            # MKA: The package will be dynamic and not a packaged service product; otherwise, the used amount should be considered as zero.
            if not (move.acs_package_id.package_type == 'fixed' and move.acs_package_id.product_id):
                used_amount = sum(move.acs_package_invoice_line_ids.mapped('price_total'))
            move.acs_used_amount = used_amount

    def acs_compute_remaining_amount(self):
        for move in self:
            remaining_amount = 0.0
            # MKA: The package will be dynamic and not a packaged service product; otherwise.
            # The remaining amount will be calculated based on the package total and the used amount.
            if not (move.acs_package_id.package_type == 'fixed' and move.acs_package_id.product_id):
                remaining_amount = move.acs_package_total_amount - move.acs_used_amount
            move.acs_remaining_amount = remaining_amount

    acs_package_id = fields.Many2one('acs.hms.package', 'Package')
    acs_package_invoice_line_ids = fields.One2many('acs.package.invoice.line', 'move_id', 'ACS Package Invoice Lines')
    acs_package_total_amount = fields.Monetary(string='Package Total Amount', compute="acs_compute_package_amount", store=True)
    acs_used_amount = fields.Monetary(string='Used Amount', compute='acs_compute_used_amount')
    acs_remaining_amount = fields.Monetary(string='Remaining Amount', compute='acs_compute_remaining_amount')

    def acs_prepare_invoice_line(self, product, quantity, price_unit, uom_id, account_id, tax_ids,
        name=None, discount=0.0, move_id=None, acs_package_id=None):
        return {
            'product_id': product.id,
            'name': name or product.name,
            'price_unit': price_unit,
            'quantity': quantity,
            'product_uom_id': uom_id,
            'account_id': account_id,
            'tax_ids': [Command.set(tax_ids)],
            'discount': discount,
            **({'move_id': move_id} if move_id else {}),
            **({'acs_package_id': acs_package_id} if acs_package_id else {})
        }
    
    def acs_prepare_package_inv_line(self, move, package, package_line, remaining_qty):
        self.env['acs.package.invoice.line'].sudo().create({
            'move_id': move.id,
            'package_id': package.id,
            'product_id': package_line.product_id.id,
            'price_unit': package_line.price_unit or 0.0,
            'allowed_qty': package_line.product_uom_qty,
            'remaining_qty': remaining_qty,
            'product_uom_qty': package_line.product_uom_qty,
            'product_uom_id': package_line.product_uom_id.id,
            'discount': package_line.discount,
            'tax_id': [Command.set(package_line.tax_id.ids)],
        })

    def acs_get_line_section(self, name=None):
        return {'name': name, 'display_type': 'line_section'}
    
    def acs_get_package_invoice_lines(self):
        for move in self:
            invoice_lines_to_delete = self.env['account.move.line']

            package = move.acs_package_id
            if not package:
                return True

            move.invoice_line_ids.filtered(lambda l: l.display_type == 'line_section').unlink()

            # Fixed Package with product_id (single service product line)
            if package.package_type == 'fixed':
                if package.product_id:
                    account_id = package.product_id._get_product_accounts().get('income')
                    move.write({
                        'invoice_line_ids': [
                            Command.clear(),
                            Command.create(self.acs_get_line_section('Package')),
                            Command.create(self.acs_prepare_invoice_line(
                                package.product_id, 1.0, package.service_amount or 0.0,
                                package.product_id.uom_id.id, account_id.id,
                                package.product_id.taxes_id._filter_taxes_by_company(move.company_id).ids,
                                name=package.product_id.name
                            ))
                        ]
                    })

                elif package.order_line:
                    line_vals = [Command.create(self.acs_get_line_section('Package Items'))]
                    for package_line in package.order_line:
                        product = package_line.product_id
                        account_id = product._get_product_accounts().get('income')

                        line_vals.append(Command.create(
                            self.acs_prepare_invoice_line(
                                product, package_line.product_uom_qty, package_line.price_unit,
                                package_line.product_uom_id.id, account_id.id,
                                package_line.tax_id.ids, name=product.name
                            )
                        ))
                    move.write({'invoice_line_ids': [Command.clear()] + line_vals})

                # MKA: Only the package template data is being created for the package invoice line.
                for package_line in package.order_line:
                    self.acs_prepare_package_inv_line(move, package, package_line, 0.0)

            else:
                package_inv_lines_vals = []
                used_qty_list = []
                package_products = package.order_line.mapped('product_id.id')
                package_prod_map = {l.product_id.id: l for l in package.order_line}
                extra_charge_lines = []

                for inv_line in move.invoice_line_ids.filtered(lambda l: l.product_id and l.product_id.id in package_products):
                    product_id = inv_line.product_id.id
                    package_line = package_prod_map[product_id]
                    allowed_qty = package_line.product_uom_qty or 0.0
                    invoice_qty = inv_line.quantity

                    already_used_qty = sum(u['used_qty'] for u in used_qty_list if u['product_id'] == product_id)
                    available_qty = allowed_qty - already_used_qty

                    if available_qty <= 0:
                        used_qty = 0.0
                        remaining_qty = invoice_qty
                    elif invoice_qty <= available_qty:
                        used_qty = invoice_qty
                        remaining_qty = 0.0
                    else:
                        used_qty = available_qty
                        remaining_qty = invoice_qty - available_qty

                    for line in used_qty_list:
                        if line['product_id'] == product_id:
                            line['used_qty'] += used_qty
                            break
                    else:
                        used_qty_list.append({'product_id': product_id, 'used_qty': used_qty})

                    package_invoice_line = self.env['acs.package.invoice.line'].sudo().search([
                        ('move_id', '=', move.id),
                        ('package_id', '=', package.id),
                        ('product_id', '=', inv_line.product_id.id)
                    ], limit=1)

                    # MKA: Only the package template data is being created for the package invoice line.
                    if not package_invoice_line:
                        for package_line in package.order_line:
                            self.acs_prepare_package_inv_line(move, package, package_line, remaining_qty)

                    if remaining_qty > 0:
                        inv_line.quantity = remaining_qty
                        extra_charge_lines.append(inv_line)
                    else:
                        invoice_lines_to_delete |= inv_line

                # Package line section
                # Dynamic Package with always Service Product
                account_id = package.product_id._get_product_accounts().get('income')
                package_inv_lines_vals += [
                    Command.create(self.acs_get_line_section('Package')),
                    Command.create(self.acs_prepare_invoice_line(
                        package.product_id, 1.0, package.product_id.list_price,
                        package.product_id.uom_id.id, account_id.id,
                        package.product_id.taxes_id._filter_taxes_by_company(move.company_id).ids,
                        move_id=move.id, acs_package_id=package.id,
                        name=package.product_id.name
                    ))
                ]

                # Build Extra Charges section
                package_inv_charges_line = move.invoice_line_ids.filtered(lambda l: l.product_id and l.product_id.id not in package_products and l not in invoice_lines_to_delete)
                invoice_all_final_line = extra_charge_lines + list(package_inv_charges_line)

                if invoice_all_final_line:
                    package_inv_lines_vals.append(Command.create(self.acs_get_line_section('Extra Charges')))
                    for inv_line in invoice_all_final_line:
                        package_inv_lines_vals.append(Command.create(
                            self.acs_prepare_invoice_line(
                                inv_line.product_id, inv_line.quantity, inv_line.price_unit,
                                inv_line.product_uom_id.id, inv_line.account_id.id,
                                inv_line.tax_ids.ids, name=inv_line.name, discount=inv_line.discount
                            )
                        ))
                        invoice_lines_to_delete |= inv_line

                if package_inv_lines_vals:
                    move.write({'invoice_line_ids': package_inv_lines_vals})

                if invoice_lines_to_delete:
                    invoice_lines_to_delete.unlink()

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    acs_package_id = fields.Many2one('acs.hms.package', string='Package')

    # ---------------------------- Please Do Not Touch and Remove These Fields ----------------------------
    acs_hms_source_type = fields.Selection(selection_add=[('procedure',), ('surgery','Surgery')])
    
    acs_surgery_ids = fields.Many2many("hms.surgery", "rel_acs_surgery_move_line", 
                                       "move_line_id", "surgery_id", string="Surgery")
    # -----------------------------------------------------------------------------------------------------