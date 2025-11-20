# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AcsSchedule(models.Model):
    _inherit = "acs.schedule"

    schedule_type = fields.Selection(selection_add=[('radiology','Radiology')])
    radiology_room_id = fields.Many2one('acs.radiology.room', string="Radiology Room")


class AcsScheduleSlotLines(models.Model):
    _inherit = 'acs.schedule.slot.lines'

    @api.depends('radiology_request_ids','radiology_request_ids.state')
    def get_acs_remaining_limit(self):
        super().get_acs_remaining_limit()
        for slot in self.sudo():
            if slot.acs_slot_id.acs_schedule_id.schedule_type=='radiology':
                linked_records = len(self.env['acs.radiology.request'].sudo().search([('schedule_slot_id','=',slot.id),('state','!=','canceled')]))
                slot.rem_limit = slot.limit - linked_records

    radiology_request_ids = fields.One2many('acs.radiology.request', 'schedule_slot_id', string="Radiology Requests")
    schedule_type = fields.Selection(selection_add=[('radiology','Radiology')])

    def acs_book_appointment(self):
        action = super().acs_book_appointment()
        if self.schedule_type=='radiology':
            action = self.env["ir.actions.actions"]._for_xml_id("acs_radiology.hms_action_radiology_request")
            action['context'] = {
                'default_schedule_date': self.acs_slot_id.slot_date,
                'default_date': self.from_slot,
                'default_schedule_slot_id': self.id
            }
            action['views'] = [(self.env.ref('acs_radiology.patient_radiology_test_request_form').id, 'form')]
        return action
