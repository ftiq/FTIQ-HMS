# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields
from datetime import time, date, datetime, timedelta
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT
import math
from pytz import timezone, utc
from odoo.tools.float_utils import float_round

def float_to_time(hours):
    """ Convert a number of hours into a time object. """
    if hours == 24.0:
        return time.max
    fractional, integral = math.modf(hours)
    int_fractional = int(float_round(60 * fractional, precision_digits=0))
    if int_fractional > 59:
        integral += 1
        int_fractional = 0
    return time(int(integral), int_fractional, 0)


class AcsMedicationPlanningLine(models.TransientModel):
    _name = 'acs.medication.plan.line'
    _description = 'Medication Plan Line'

    wizard_id = fields.Many2one("acs.medication.plan.wiz")
    product_id = fields.Many2one("product.product", "Product", required=True)
    dose = fields.Float('Dosage', help="Amount of medication (eg, 250 mg) per dose", default=1.0)
    allowed_uom_ids = fields.Many2many('uom.uom', compute='_compute_allowed_uom_ids')
    dosage_uom_id = fields.Many2one('uom.uom', string='Unit of Dosage', help='Amount of Medicine (eg, mg) per dose', domain="[('id', 'in', allowed_uom_ids)]")
    form_id = fields.Many2one('drug.form',related='product_id.form_id', string='Form',help='Drug form, such as tablet or gel')
    route_id = fields.Many2one('drug.route', ondelete="cascade", string='Route', help='Drug form, such as tablet or gel')
    short_comment = fields.Char(string='Comment', help='Short comment on the specific drug')
    acs_medication_time_ids = fields.Many2many('acs.medication.time', 'acs_medication_time_wizard_rel', 'wizard_id', 'time_id', string='Medication Times')
    days = fields.Float('Days', default=1.0, help="Number of days for which the medication is planned")

    @api.depends('product_id', 'product_id.uom_id', 'product_id.uom_ids')
    def _compute_allowed_uom_ids(self):
        for line in self:
            line.allowed_uom_ids = line.product_id.uom_id | line.product_id.uom_ids
            
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.form_id = self.product_id.form_id and self.product_id.form_id.id or False
            self.route_id = self.product_id.route_id and self.product_id.route_id.id or False
            self.dosage_uom_id = self.product_id.dosage_uom_id and self.product_id.dosage_uom_id.id or self.product_id.uom_id.id
            self.dose = self.product_id.dosage or 1
            self.short_comment = self.product_id.short_comment
            self.acs_medication_time_ids = self.product_id.common_dosage_id.acs_medication_time_ids.ids


class AcsMedicationPlanning(models.TransientModel):
    _name = 'acs.medication.plan.wiz'
    _description = "Medication Planning"

    hospitalization_id = fields.Many2one('acs.hospitalization', string='Hospitalization', required=True)
    patient_id = fields.Many2one('hms.patient', string='Patient', related='hospitalization_id.patient_id')
    physician_id = fields.Many2one('hms.physician', string='Physician')
    line_ids = fields.One2many('acs.medication.plan.line', 'wizard_id', string='Medication Lines')
    start_date = fields.Date('Start Date', required=True, default=fields.Datetime.today())

    @api.onchange('cancel_reason_id')
    def onchange_reason(self):
        if self.cancel_reason_id:
            self.cancel_reason = self.cancel_reason_id.name

    def create_planning(self):
        tz = timezone(self.env.user.tz)
        combine = datetime.combine

        for line in self.line_ids:
            start_date = self.start_date 
            for day in range(int(line.days)):
                data = {
                    'physician_id': self.physician_id.id,
                    'hospitalization_id': self.hospitalization_id.id,
                    'patient_id': self.patient_id.id,
                    'product_id': line.product_id.id,
                    'dose': line.dose,
                    'dosage_uom_id': line.dosage_uom_id.id,
                    'form_id': line.form_id.id,
                    'route_id': line.route_id.id,
                    'short_comment': line.short_comment,
                }
                for time in line.acs_medication_time_ids:
                    time_hour_from = float_to_time(time.acs_time)
                    # hours are interpreted in the resource's timezone
                    data['date'] = tz.localize(combine(start_date, time_hour_from)).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    self.env['acs.patient.medication'].create(data)
                start_date = start_date + timedelta(days=1)
