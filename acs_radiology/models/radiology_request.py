# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class PatientRadiologyTestLine(models.Model):
    _name = "radiology.request.line"
    _description = "Test Lines"

    @api.depends('quantity', 'sale_price', 'tax_ids')
    def _compute_amount(self):
        for line in self:
            taxes_res = line.tax_ids.compute_all(
                line.sale_price,
                line.company_id.currency_id,
                line.quantity,
                line.test_id.product_id,
                line.radiology_request_id.patient_id.partner_id)
            line.amount_total = taxes_res['total_included'] if taxes_res else 0.0
            line.tax_amount = taxes_res['total_included'] - taxes_res['total_excluded'] if taxes_res else 0.0

    @api.depends('test_id')
    def _acs_is_manager(self):
        is_manager = self.env.user.has_group('acs_radiology.group_hms_radiology_manager')
        for rec in self:
            rec.is_manager = is_manager

    name = fields.Char(string="Description")
    sequence = fields.Integer("Sequence", default=10)
    test_id = fields.Many2one('acs.radiology.test',string='Test', ondelete='cascade')
    acs_tat = fields.Char(related='test_id.acs_tat', string='Turnaround Time', readonly=True)
    instruction = fields.Char(string='Special Instructions')
    radiology_request_id = fields.Many2one('acs.radiology.request',string='Lines', ondelete='cascade')
    sale_price = fields.Float(string='Sale Price')
    tax_ids = fields.Many2many('account.tax', 'radiology_request_line_tax_rel', 'line_id', 'tax_ids', string='Taxes')
    tax_amount = fields.Float(compute="_compute_amount", string="Tax Amount", store=True)
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company',related='radiology_request_id.company_id') 
    quantity = fields.Integer(string='Quantity', default=1)
    amount_total = fields.Float(compute="_compute_amount", string="Subtotal", store=True)
    parent_line_id = fields.Many2one('radiology.request.line',string='Parent Line', ondelete='cascade', copy=False)
    patient_radiology_ids = fields.Many2many('patient.radiology.test', 'radiology_request_line_test_rel', 'req_line_id', 'patient_radiology_test_id', 'Radiology Tests', ondelete='cascade')
    is_manager = fields.Boolean(compute=_acs_is_manager)
    display_type = fields.Selection([
        ('product', "Product"),
        ('line_section', "Section"),
        ('line_note', "Note")], help="Technical field for UX purpose.", default='product')

    @api.onchange('test_id')
    def onchange_test(self):
        if self.test_id:
            price = 0.0
            if self.radiology_request_id.pricelist_id:
                price = self.radiology_request_id.pricelist_id._get_product_price(self.test_id.product_id, 1)
            elif self.radiology_request_id.patient_id.property_product_pricelist:
                price = self.radiology_request_id.patient_id.property_product_pricelist._get_product_price(self.test_id.product_id, 1)
            else:
                price = self.test_id.product_id.lst_price
            self.sale_price = price
            self.instruction = self.test_id.instruction

            taxes_ids = self.test_id.product_id.taxes_id._filter_taxes_by_company(self.company_id)
            self.tax_ids = [Command.set(taxes_ids.ids)]

            product = self.test_id.product_id
            taxes = product.taxes_id.compute_all(self.sale_price, self.company_id.currency_id, self.quantity, self.test_id.product_id, self.radiology_request_id.patient_id.partner_id)
            self.amount_total = taxes.get('total_included', 0.0)
            self.tax_amount = taxes.get('total_included', 0.0) - taxes.get('total_excluded', 0.0)
            self.name = self.test_id.name + (self.test_id.description or '')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if not self.env.context.get('avoid_subsequent_test'):
            for record in res:
                for sub_seq_test in record.test_id.subsequent_test_ids:
                    sub_line = self.with_context(avoid_subsequent_test=True).create({
                        'parent_line_id': record.id,
                        'test_id': sub_seq_test.id,
                        'radiology_request_id': record.radiology_request_id.id,
                    })
                    sub_line.onchange_test()
        return res


class RadiologyRequest(models.Model):
    _name = 'acs.radiology.request'
    _description = 'Radiology Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'acs.hms.mixin', 'portal.mixin']
    _order = 'date desc, id desc'

    @api.depends('line_ids','line_ids.amount_total')
    def _get_total_price(self):
        for rec in self:
            rec.untaxed_amount_total = sum(line.sale_price for line in rec.line_ids)
            rec.tax_amount_total = sum(line.tax_amount for line in rec.line_ids)
            rec.total_price = sum(line.amount_total for line in rec.line_ids)

    @api.depends('patient_id', 'patient_id.birthday', 'date')
    def get_patient_age(self):
        for rec in self:
            age = ''
            if rec.patient_id.birthday:
                end_data = rec.date or fields.Datetime.now()
                delta = relativedelta(end_data, rec.patient_id.birthday)
                if delta.years <= 2:
                    age = str(delta.years) + _(" Year") + str(delta.months) + _(" Month ") + str(delta.days) + _(" Days")
                else:
                    age = str(delta.years) + _(" Year")
            rec.patient_age = age
    
    @api.model
    def _get_default_acs_no_radiology_result(self):
        return self.env.company.acs_no_radiology_result

    def _acs_rec_count(self):
        for rec in self:
            rec.invoice_count = len(self.acs_radiology_req_invoices())

    name = fields.Char(string='Request Number', readonly=True, index=True, copy=False, tracking=True,default='New')
    notes = fields.Text(string='Notes')
    date = fields.Datetime('Date', required=True, default=fields.Datetime.now(), tracking=True)
    state = fields.Selection([
        ('draft','Draft'),
        ('requested','Requested'),
        ('accepted','Accepted'),
        ('in_progress','In Progress'),
        ('to_invoice','To Invoice'),
        ('done','Done'),
        ('cancel','Cancel'),],
        string='Status',readonly=True, default='draft', tracking=True)
    patient_id = fields.Many2one('hms.patient', string='Patient', required=True, ondelete='restrict', tracking=True)
    patient_age = fields.Char(compute="get_patient_age", string='Age', store=True,
        help="Computed patient age at the time of the request")
    physician_id = fields.Many2one('hms.physician',
        string='Prescribing Doctor', help="Doctor who Requested the test.", ondelete='restrict', tracking=True)
    invoice_id = fields.Many2one('account.move',string='Invoice', copy=False)
    radiology_bill_id = fields.Many2one('account.move',string='Vendor Bill', copy=False)
    line_ids = fields.One2many('radiology.request.line', 'radiology_request_id',
        string='Radiology Test Line', copy=True)
    invoice_exempt = fields.Boolean(string='Invoice Exempt', readonly=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self.env.company.currency_id.id)
    untaxed_amount_total = fields.Float(compute=_get_total_price, string='Untaxed Amount', store=True)
    tax_amount_total = fields.Float(compute=_get_total_price, string='Taxes', store=True)
    total_price = fields.Float(compute=_get_total_price, string='Total', store=True)
    info = fields.Text(string='Extra Info')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', default=lambda self: self.env.company)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', check_company=True, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, related invoice will be affected.")
    payment_state = fields.Selection(related="invoice_id.payment_state", store=True, string="Payment Status")
    radiology_group_id = fields.Many2one('radiology.group', ondelete="set null", string='Test Group')
    acs_radiology_invoice_policy = fields.Selection(related="company_id.acs_radiology_invoice_policy")

    #Just to make object selectable in selection field this is required: Waiting Screen
    acs_show_in_wc = fields.Boolean(default=True)
    is_group_request = fields.Boolean()
    group_patient_ids = fields.Many2many("hms.patient", "hms_patient_radiology_req_rel", "radiology_request_id", "patient_id", string="Other Group Patients")
    patient_test_ids = fields.One2many('patient.radiology.test', 'radiology_request_id', string='Test Results')

    invoice_ids = fields.One2many('account.move', 'radiology_request_id', string='Invoices')
    invoice_count = fields.Integer(compute='_acs_rec_count', string='# Invoices')
    acs_show_create_invoice = fields.Boolean(compute="get_acs_show_create_invoice", string="Show Create Invoice Button")
    radiology_room_id = fields.Many2one('acs.radiology.room', ondelete='cascade', 
        string='Room (Cabin)', help="Radiology Room", copy=False)
    acs_no_radiology_result = fields.Boolean(string="No Radiology Result", default=_get_default_acs_no_radiology_result)
    referring_partner_id = fields.Many2one('res.partner', string="Referred By")
    other_radiology = fields.Boolean(string='Send to Other Radiology')
    radiology_id = fields.Many2one('acs.radiology', ondelete='restrict', string='Radiology')

    move_line_ids = fields.Many2many("account.move.line", "rel_acs_radiology_req_move_line", 
                                    "radiology_request_id", "move_line_id", string="Move Lines")
    
    #ACS: Compute visibility of create invoice button.
    def get_acs_show_create_invoice(self):
        for rec in self:
            acs_show_create_invoice = False
            if not rec.invoice_id :
                if rec.state=='to_invoice':
                    acs_show_create_invoice = True
                elif rec.acs_radiology_invoice_policy=='any_time' and not rec.invoice_exempt:
                    acs_show_create_invoice = True
                elif rec.acs_radiology_invoice_policy=='in_advance' and not rec.invoice_exempt:
                    acs_show_create_invoice = True
            rec.acs_show_create_invoice = acs_show_create_invoice

    def _compute_display_name(self):
        for rec in self:
            name = rec.name or '-'
            if rec.patient_id:
                name += ' [' + rec.patient_id.name + ']'
            rec.display_name = name

    @api.onchange('radiology_group_id')
    def onchange_radiology_group(self):
        test_line_ids = []
        if self.radiology_group_id:
            for line in self.radiology_group_id.line_ids:
                test_line_ids.append((0,0,{
                    'test_id': line.test_id.id,
                    'instruction': line.instruction,
                    'sale_price' : line.sale_price,
                }))
            self.line_ids = test_line_ids

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_("Radiology Requests can be delete only in Draft state."))
        return super(RadiologyRequest, self).unlink()

    def button_requested(self):
        if not self.line_ids:
            raise UserError(_('Please add minimum one Radiology test line before submitting request.'))
        self.name = self.env['ir.sequence'].next_by_code('acs.radiology.request') or 'New'
        if self.is_group_request:
            for line in self.line_ids:
                line.quantity = len(self.group_patient_ids) + 1
        self.state = 'requested'

    def button_accept(self):
        company_id = self.sudo().company_id
        if company_id.acs_radiology_invoice_policy=='in_advance':
            if not self.invoice_id:
                raise UserError(_('Invoice is not created yet.'))
            elif self.invoice_id and company_id.acs_check_radiology_payment and self.payment_state not in ['in_payment','paid']:
                raise UserError(_('Invoice is not Paid yet.'))
        self.state = 'accepted'

    def prepare_test_result_data(self, line, patient):
        parent_test_id = False
        if line.parent_line_id and line.parent_line_id.patient_radiology_ids:
            parent_test_ids = line.parent_line_id.patient_radiology_ids.filtered(lambda lt: lt.patient_id==patient)
            if parent_test_ids:
                parent_test_id = parent_test_ids[0].id

        res = {
            'patient_id': patient.id,
            'physician_id': self.physician_id and self.physician_id.id,
            'test_id': line.test_id.id,
            'user_id': self.env.user.id,
            'date_requested': self.date,
            'radiology_request_id': self.id,
            'parent_test_id': parent_test_id,
            'diagnosis': line.test_id.diagnosis
        }
        return res

    def button_in_progress(self):
        self.state = 'in_progress'
        if not self.acs_no_radiology_result:
            RadiologyTest = self.env['patient.radiology.test']
            Consumable = self.env['hms.consumable.line']

            patients = self.mapped('patient_id') + self.mapped('group_patient_ids')
            for line in self.line_ids.filtered(lambda l: l.display_type == 'product'):
                for patient in patients:
                    radiology_test_data = self.prepare_test_result_data(line, patient)
                    test_result = RadiologyTest.create(radiology_test_data)
                    line.patient_radiology_ids = [Command.link(test_result.id)]

                    for con_line in line.test_id.consumable_line_ids:
                        Consumable.create({
                            'patient_radiology_test_id': test_result.id,
                            'name': con_line.name,
                            'product_id': con_line.product_id and con_line.product_id.id or False,
                            'product_uom_id': con_line.product_uom_id and con_line.product_uom_id.id or False,
                            'qty': con_line.qty,
                            'date': fields.Date.today(),
                        })

    def button_done(self):
        if not self.invoice_id:
            self.state = 'to_invoice'
        else:
            self.state = 'done'

    def button_cancel(self):
        self.state = 'cancel'

    def button_draft(self):
        self.state = 'draft'

    def get_radiology_invoice_data(self, with_section=True):
        product_data = []
        if with_section:
            product_data.append({
                'name': _("Radiology Charges"),
                'display_type': 'line_section',
            })
            # Forward display_type so acs_create_invoice_line can render the invoice layout correctly
        for rec in self:
            # MKA: If an invoice is exempt, skip the radiology request test line when generating an invoice from an appointment. 
            # This is because, when an invoice is exempt, the 'Create Invoice' button is not visible in the radiology request
            if rec.invoice_exempt:
                continue
            
            for line in rec.line_ids:
                # Sections added in the precription lines will appear as subsections in the invoice
                if line.display_type in ['line_section']:
                    product_data.append({
                        'name': line.name,
                        'display_type': 'line_subsection',
                    })
                elif line.display_type in ['line_note']:
                    product_data.append({
                        'name': line.name,
                        'display_type': line.display_type,
                    })
                else:
                    product_data.append({
                        'product_id': line.test_id.product_id,
                        'price_unit': line.sale_price,
                        'quantity': line.quantity,
                        'tax_ids': line.tax_ids,
                        'acs_hms_source_type': 'radiology',
                        'acs_radiology_request_ids': [rec.id]
                    })
        return product_data

    def create_invoice(self):
        if not self.line_ids:
            raise UserError(_("Please add Radiology Tests first."))

        product_data = self.get_radiology_invoice_data()
        acs_context = {}
        if self.pricelist_id:
            acs_context.update({'acs_pricelist_id': self.pricelist_id.id})
        if self.physician_id:
            acs_context.update({'commission_partner_ids':self.physician_id.partner_id.id})
        inv_data = {
            'hospital_invoice_type': 'radiology',
            'physician_id': self.physician_id and self.physician_id.id or False,
            'radiology_request_id': self.id
        }
        invoice = self.with_context(acs_context).acs_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        self.invoice_id = invoice.id
        if self.state == 'to_invoice':
            self.state = 'done'

    def acs_radiology_req_invoices(self):
        """
            MKA: It will return the invoice if the radiology is linked to an invoice line. 
            If it's not found in the invoice lines, it will then check the invoice itself. 
        """
        line_invoice = self.move_line_ids.mapped('move_id')
        direct_invoice = self.invoice_ids
        final_invoice = (line_invoice | direct_invoice)
        return final_invoice

    def create_radiology_bill(self):
        if not self.line_ids:
            raise UserError(_("Please add lab Tests first."))

        product_data = []
        for line in self.line_ids:
            product_data.append({
                'product_id': line.test_id.product_id,
                'price_unit': line.test_id.product_id.standard_price,
            })

        inv_data={'move_type': 'in_invoice'}
        bill = self.acs_create_invoice(partner=self.radiology_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        self.radiology_bill_id = bill.id
        bill.radiology_request_id = self.id

    def view_invoice(self):
        invoices = self.acs_radiology_req_invoices()
        action = self.acs_action_view_invoice(invoices)
        return action

    def action_view_test_results(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_radiology.action_radiology_result")
        action['domain'] = [('radiology_request_id','=',self.id)]
        action['context'] = {'default_radiology_request_id': self.id, 'default_physician_id': self.physician_id.id}
        return action

    def _acs_get_report_base_filename(self):
        if not self.patient_test_ids:
            raise UserError(_("There are no linked results to print."))
        return (self.name or 'RadiologyResults').replace('/','_') + '_RadiologyResults'

    def acs_update_price(self):
        for line in self.line_ids:
            line.onchange_test()

    def action_radiology_req_send(self):
        '''
        This function opens a window to compose an email, with the template message loaded by default
        '''
        self.ensure_one()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('acs_radiology.acs_radiology_req_email', raise_if_not_found=False)
        ctx = {
            'default_model': 'acs.radiology.request',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_sendmail(self):
        '''
        This function opens a window to compose an email, with the template message loaded by default
        '''
        self.ensure_one()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('acs_radiology.acs_other_radiology_req_email', raise_if_not_found=False)
        ctx = {
            'default_model': 'acs.radiology.request',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    #method to create get invoice data and set passed invoice id.
    def acs_common_invoice_radiology_data(self, invoice_id=False):
        data = []
        if self.ids:
            data = self.get_radiology_invoice_data()
            if invoice_id:
                self.invoice_id = invoice_id.id
        return data
    
    def _compute_access_url(self):
        super()._compute_access_url()
        for rec in self:
            rec.access_url = '/my/radiology_requests/%s' % (rec.id)

    @api.onchange('patient_id')
    def onchange_patient_id_set_referring_doctor(self):
        referring_partner = self.acs_get_referring_partner(self.patient_id, referral_type='radiology')
        if referring_partner:
            self.referring_partner_id = referring_partner.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: