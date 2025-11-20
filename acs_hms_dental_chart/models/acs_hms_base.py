# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.tools import format_datetime as tool_format_datetime
from odoo.fields import Command

import json
import logging
_logger = logging.getLogger(__name__)

class HmsPatient(models.Model):
    _inherit = 'hms.patient'

    @api.model
    def acs_get_patient_teeth_data(self, patient_id):
        if not patient_id:
            return {}

        patient = self.browse(patient_id)
        data = {}

        try:
            patient_id = int(patient_id)
        except (ValueError, TypeError):
            return data

        patient = self.env['hms.patient'].browse(patient_id)
        if not patient.exists():
            return data

        procedures = patient.patient_procedure_ids.filtered(lambda t: t.tooth_ids).sorted(key=lambda t: t.id)
        for procedure in procedures:
            is_schedule = procedure.state == 'scheduled'
            is_running = procedure.state == 'running'
            is_done = procedure.state == 'done'
            is_cancel = procedure.state == 'cancel'
            is_removed = procedure.product_id.dental_procedure_type == 'tooth_removal'
            for tooth in procedure.tooth_ids:
                data[tooth.id] = {
                    'procedure_details': f"{procedure.product_id.name} [{procedure.name}]",
                    'show_procedure_image': procedure.product_id.image_1920 if procedure.product_id.show_image_in_chart else False,
                }
                if is_schedule:
                    data[tooth.id]['procedure_schedule'] = True
                if is_running:
                    data[tooth.id]['procedure_running'] = True
                if is_done:
                    data[tooth.id]['procedure_done'] = True
                if is_cancel:
                    data[tooth.id]['procedure_cancel'] = True
                if is_removed:
                    data[tooth.id]['procedure_remove'] = True

        for tooth_id, val in data.items():
            val['procedure_details'] = "Performed Procedure:\n" + val['procedure_details']
        return data

class ACSProduct(models.Model):
    _inherit = 'product.template'

    dental_procedure_type = fields.Selection([('tooth_removal','Remove Tooth'),('Other','Other')])
    show_image_in_chart = fields.Boolean('Show Product Image in Chart', 
                                         help="Image to show in chart instead of tooth when perfomed this procedure.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

