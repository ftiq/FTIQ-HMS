# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AcsBillSheet(models.Model):
    _name = 'acs.bill.sheet'
    _description = 'Bill Sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'acs.hms.mixin']
    _order = "id desc"

    name = fields.Char(string='Name', readonly=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='Status', copy=False, default='draft', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', index=True, required=True, tracking=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    date_from = fields.Date(required=True, 
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(required=True,
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id, required=True, tracking=True)

    note = fields.Text("Note")
    company_id = fields.Many2one('res.company',
        string='Hospital', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id",
        string='Currency')
    amount_total = fields.Monetary(compute="_amount_all", string="Total")
    bill_ids = fields.One2many('account.move', 'acs_bill_sheet_id', string='bills')
    bill_count = fields.Integer(compute='_acs_rec_count', string='# bills')
    bill_type = fields.Selection(selection=[])

    def _acs_rec_count(self):
        for rec in self:
            rec.bill_count = len(rec.bill_ids)

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an record which is not draft or cancelled.'))
        return super(AcsBillSheet, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values['name'] = self.env['ir.sequence'].next_by_code('acs.bill.sheet')
        return super().create(vals_list)

    def action_draft(self):
        self.state = 'draft'
    
    def action_confirm(self):
        self.state = 'confirm'

    def action_cancel(self):
        self.state = 'cancel'
    
    def action_done(self):
        self.state = 'done'

    def view_bill(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice")
        action['domain'] = [('id', 'in', self.bill_ids.ids)]
        action['context'] = {}
        return action
    
    def acs_get_bill_data(self):
        return []

    def acs_create_bill(self):
        product_data = self.acs_get_bill_data()
        acs_context = {}
        bill = self.sudo().with_context(acs_context).acs_create_invoice(partner=self.partner_id, product_data=product_data, inv_data={'move_type': 'in_invoice'})
        bill.acs_bill_sheet_id = self.id
        return bill

    def acs_get_data(self):
        pass

    def _amount_all(self):
        for rec in self:
            rec.amount_total = 0.0
