# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, _,Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT


class AcsSchedulerWizard(models.TransientModel):
    _name = "acs.scheduler.wizard"
    _inherit = ['acs.scheduler.wizard','acs.hms.mixin']

    department_id = fields.Many2one('hr.department', string="Department" , domain=lambda self: self.acs_get_department_domain())
    physician_ids = fields.Many2many('hms.physician', string="Physicians")

    @api.model
    def default_get(self, fields):
        res = super(AcsSchedulerWizard, self).default_get(fields)
        if self.env.user.sudo().physician_ids:
            res['physician_ids'] = self.env.user.sudo().physician_ids
        return res

    @api.onchange('schedule_id')
    def onchange_schedule(self):
        super(AcsSchedulerWizard, self).onchange_schedule()
        if self.schedule_id and self.schedule_id.id and self.schedule_id.company_id and self.schedule_id.schedule_type=='appointment':
            company_id = self.schedule_id.sudo().company_id
            self.booking_slot_time = company_id.hms_app_booking_slot_time
            self.acs_allowed_booking_per_slot = company_id.hms_app_allowed_booking_per_slot
            self.department_id = self.schedule_id.department_id and self.schedule_id.department_id.id or False
            self.physician_ids = [Command.set(self.schedule_id.physician_ids.ids)]
    
    def get_slot_args(self):
        slot_args = super(AcsSchedulerWizard, self).get_slot_args()
        slot_args.update({
            'physician_ids': self.physician_ids, 
            'department_id': self.department_id
        })
        return slot_args

class AcsBlockSlotWizard(models.TransientModel):
    _name = "acs.block.slots.wizard"
    _inherit = ['acs.block.slots.wizard','acs.hms.mixin']

    department_id = fields.Many2one('hr.department', string="Department" , domain=lambda self: self.acs_get_department_domain())
    physician_ids = fields.Many2many('hms.physician', string="Physicians")

    @api.onchange('schedule_id')
    def onchange_schedule(self):
        super().onchange_schedule()        
        self.department_id = self.schedule_id.department_id and self.schedule_id.department_id.id or False
        self.physician_ids = [Command.set(self.schedule_id.physician_ids.ids)]
    
    def acs_get_domain(self):
        domain = super().acs_get_domain()
        if self.department_id:
            domain.append(('department_id', 'in', self.department_id.ids))
        if self.physician_ids:
            domain.append(('physician_id', 'in', self.physician_ids.ids))
        return domain
