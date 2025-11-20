# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class Acsschedule(models.Model):
    _inherit = "acs.schedule"

    schedule_type = fields.Selection(selection_add=[('laboratory','Laboratory')])
    collection_center_id = fields.Many2one('acs.laboratory', string="Collection Center")
    physician_ids = fields.Many2many('hms.physician', 'physician_acs_schedule_rel', 'schedule_id', 'physician_id', 'Physicians')


class AcsScheduleSlotLines(models.Model):
    _inherit = 'acs.schedule.slot.lines'

    @api.depends('laboratory_request_ids','laboratory_request_ids.state')
    def get_acs_remaining_limit(self):
        super().get_acs_remaining_limit()
        for slot in self.sudo():
            if slot.acs_slot_id.acs_schedule_id.schedule_type=='laboratory':
                linked_records = len(self.env['acs.laboratory.request'].sudo().search([('schedule_slot_id','=',slot.id),('state','!=','canceled')]))
                slot.rem_limit = slot.limit - linked_records

    laboratory_request_ids = fields.One2many('acs.laboratory.request', 'schedule_slot_id', string="Lab Requests")
    schedule_type = fields.Selection(selection_add=[('laboratory','Laboratory')])

    def acs_book_appointment(self):
        action = super().acs_book_appointment()
        if self.schedule_type=='laboratory':
            action = self.env["ir.actions.actions"]._for_xml_id("acs_laboratory.hms_action_lab_test_request")
            action['context'] = {
                'default_schedule_date': self.acs_slot_id.slot_date,
                'default_date': self.from_slot,
                'default_schedule_slot_id': self.id
            }
            action['views'] = [(self.env.ref('acs_laboratory.patient_laboratory_test_request_form').id, 'form')]
        return action
