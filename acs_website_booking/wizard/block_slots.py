# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AcsBlockSlotsWizard(models.TransientModel):
    _name = 'acs.block.slots.wizard'
    _description = 'Block Slots'

    schedule_id = fields.Many2one("acs.schedule", string="Schedule", required=True, ondelete="cascade")
    start_date = fields.Datetime('Start Date', required=True, default=fields.Datetime.now())
    end_date = fields.Datetime('End Date',required=True, default=fields.Datetime.now() + timedelta(hours=8))
    user_ids = fields.Many2many('res.users', string="Users")
    type = fields.Selection([
        ('block', 'Block'),
        ('unblock', 'Unblock')
    ], string='Action', required=True, default='block')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for wizard in self:
            if wizard.start_date > wizard.end_date:
                raise ValidationError(_("Scheduler 'Start Date' must be before 'End Date'."))
        return True

    @api.onchange('schedule_id')
    def onchange_schedule(self):
        self.user_ids = self.schedule_id.user_ids

    def acs_get_domain(self):
        domain = [('acs_schedule_id','=',self.schedule_id.id), ('from_slot','>=',self.start_date), ('to_slot','<=',self.end_date)]
        if self.user_ids:
            domain.append(('user_id', 'in', self.user_ids.ids))
        return domain

    def acs_block_slots(self):
        domain = self.acs_get_domain()
        slots = self.env['acs.schedule.slot.lines'].search(domain)
        if self.type == 'block':
            slots.action_block()
        else:
            slots.action_unblock()

