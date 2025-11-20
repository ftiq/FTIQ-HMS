# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api,fields,models,_


class AccountMove(models.Model):
    _inherit = 'account.move'

    ref_physician_id = fields.Many2one('res.partner', ondelete='restrict', string='Referring Physician', 
        index=True, help='Referring Physician')
    appointment_id = fields.Many2one('hms.appointment', string='Appointment')
    procedure_id = fields.Many2one('acs.patient.procedure', string='Patient Procedure')
    acs_treatment_id = fields.Many2one('hms.treatment', string='Patient Treatment')
    hospital_invoice_type = fields.Selection(selection_add=[('appointment', 'Appointment'), ('treatment','Treatment'), ('procedure','Procedure')])

    @api.ondelete(at_uninstall=False)
    def acs_reopen_related_appointment(self):
        appointments = self.env['hms.appointment'].search([('invoice_id', 'in', self.ids), ('state', '=', 'done')])
        for appointment in appointments:
            appointment.write({'state': 'in_consultation'})
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # ---------------------------- Please Do Not Touch and Remove These Fields ----------------------------
    acs_hms_source_type = fields.Selection(selection_add=[
        ('appointment','Appointment'), 
        ('treatment','Treatment'), 
        ('procedure','Procedure')
    ])
    
    acs_appointment_ids = fields.Many2many("hms.appointment", "rel_acs_appointment_move_line", 
                                           "move_line_id", "appointment_id", string="Appointment")
    
    acs_procedure_ids = fields.Many2many("acs.patient.procedure", "rel_acs_procedure_move_line", 
                                         "move_line_id", "procedure_id", string="Procedure")
    
    acs_treatment_ids = fields.Many2many("hms.treatment", "rel_acs_treatment_move_line", 
                                         "move_line_id", "treatment_id", string="Treatment")
    # -----------------------------------------------------------------------------------------------------