# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    acs_bill_sheet_id = fields.Many2one("acs.bill.sheet", string="Bill Sheet")