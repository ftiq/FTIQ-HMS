# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError


class HmsAppointment(models.Model):
    _inherit = 'hms.appointment'

    video_call_link = fields.Char(related="acs_calendar_event_id.videocall_location", string="Video Call Link", readonly=True)

    def acs_prepare_calendar_data(self):
        data = super().acs_prepare_calendar_data()
        data.update({
            'partner_ids': [Command.set([self.patient_id.partner_id.id, self.physician_id.partner_id.id])],
        })
        return data
    
    def create_video_call_link(self):
        if not self.acs_calendar_event_id:
            self.acs_calendar_event('physician_id')
        self.is_video_call = True
        self.acs_calendar_event_id.with_context(acs_avoid_check=True)._set_discuss_videocall_location()

    def appointment_confirm(self):
        super(HmsAppointment, self).appointment_confirm()
        if self.is_video_call:
            self.acs_calendar_event_id.with_context(acs_avoid_check=True)._set_discuss_videocall_location()
            template = self.env.ref('acs_hms_video_call.acs_video_call_invitaion')
            template.sudo().send_mail(self.id, raise_exception=False)

    def get_partner_ids(self):
        partner_ids = ','.join(map(lambda x: str(x.id), [self.patient_id.partner_id,self.physician_id.partner_id]))
        return partner_ids

    def action_send_invitaion(self):
        '''
        This function opens a window to compose an email, with the template message loaded by default
        '''
        if not self.acs_calendar_event_id:
            self.create_video_call_link()

        self.ensure_one()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('acs_hms_video_call.acs_video_call_invitaion', raise_if_not_found=False)
        ctx = {
            'default_model': 'hms.appointment',
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

