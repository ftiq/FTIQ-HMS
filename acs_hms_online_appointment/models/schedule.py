# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _,Command
from odoo.exceptions import UserError

class AcsSchedule(models.Model):
    _inherit = "acs.schedule"

    schedule_type = fields.Selection(selection_add=[('appointment','Appointment')])
    physician_ids = fields.Many2many('hms.physician', 'physician_schedule_rel', 'schedule_id', 'physician_id', 'Physicians')

    @api.model
    def default_get(self, fields):
        res = super(AcsSchedule, self).default_get(fields)
        if self.env.user.sudo().physician_ids:
            res['physician_ids'] = [Command.set(self.env.user.sudo().physician_ids.ids)]
        return res


class AcsScheduleSlot(models.Model):
    _inherit = "acs.schedule.slot"

    def acs_get_slot_line_data(self, slot, from_slot, to_slot, **kw):
        line_data = super().acs_get_slot_line_data(slot, from_slot, to_slot, **kw)
        if kw.get('physician_id'):
            line_data['physician_id'] = kw.get('physician_id').id
        if kw.get('department_id'):
            line_data['department_id'] = kw.get('department_id').id
        return line_data
    
    def acs_get_resources(self, schedule, **kw):
        field_name, resources = super().acs_get_resources(schedule, **kw)
        physician_ids = kw.get('physician_ids')
        if not physician_ids and schedule.physician_ids and schedule.schedule_type=='appointment':
            physician_ids = schedule.physician_ids
        if physician_ids:
            resources = schedule.physician_ids
            field_name = 'physician_id'
        return field_name, resources

class AcsScheduleSlotLines(models.Model):
    _name = 'acs.schedule.slot.lines'
    _inherit = ['acs.schedule.slot.lines','acs.hms.mixin']

    @api.depends('appointment_ids','appointment_ids.state')
    def get_acs_remaining_limit(self):
        super().get_acs_remaining_limit()
        for slot in self.sudo():
            if slot.acs_slot_id.acs_schedule_id.schedule_type=='appointment':
                linked_records = len(self.env['hms.appointment'].sudo().search([('schedule_slot_id','=',slot.id),('state','not in',['draft','cancel'])]))
                slot.rem_limit = slot.limit - linked_records

    physician_id = fields.Many2one('hms.physician', string='Physician', index=True)
    department_id = fields.Many2one('hr.department', domain=lambda self: self.acs_get_department_domain())
    appointment_ids = fields.One2many('hms.appointment', 'schedule_slot_id', string="Appointment")
    schedule_type = fields.Selection(selection_add=[('appointment','Appointment')])

    def acs_book_appointment(self):
        action = super().acs_book_appointment()
        if self.schedule_type=='appointment':
            action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.action_appointment")
            action['context'] = {
                'default_department_id': self.department_id.id, 
                'default_physician_id': self.physician_id.id,
                'default_schedule_date': self.acs_slot_id.slot_date,
                'default_date': self.from_slot,
                'default_date_to': self.to_slot,
                'default_schedule_slot_id': self.id,            
            }
            action['views'] = [(self.env.ref('acs_hms.view_hms_appointment_form').id, 'form')]
        return action

    def unlink(self):
        for rec in self:
            if rec.appointment_ids:
                raise UserError(_('You can not delete slot which already have booked appointments.'))
        return super(AcsScheduleSlotLines, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: