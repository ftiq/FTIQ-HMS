# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import secrets


class AcsHmsWaitingScreen(models.Model):
    _name = 'acs.hms.waiting.screen'
    _description = "Waiting Screen"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Screen Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    res_model_id = fields.Many2one('ir.model', string='Model', ondelete="cascade", required=True)
    physician_ids = fields.Many2many('hms.physician', 'hms_physician_waiting_screen_rel','physician_id', 'screen_id', string='Physicians')
    company_id = fields.Many2one('res.company', ondelete="cascade", string='Hospital',default=lambda self: self.env.company)
    show_patient_name_image = fields.Boolean("Show Patient Name & Image", default=True)
    show_cabin = fields.Boolean("Show Cabin", default=True)
    acs_refresh_time = fields.Integer("Refresh Time (Seconds)", default=5)
    acs_number_of_records = fields.Integer("Shown Number of Records", default=5)
    in_progress_state = fields.Char("In-Progress State", default="in_consultation")
    in_progress_color = fields.Char(string='In-Progress Color', default="#d9534f")

    acs_physician_field_id = fields.Many2one('ir.model.fields','Physician', ondelete='cascade', domain="['&',('ttype', '=', 'many2one'),('model_id','=',res_model_id)]", required=True,
        help="Physician Field shown on waiting screen: If no physician in object user can be also shown.")
    acs_patient_field_id = fields.Many2one('ir.model.fields','Patient', ondelete='cascade', domain="['&',('ttype', '=', 'many2one'),('model_id','=',res_model_id)]")
    acs_cabin_field_id = fields.Many2one('ir.model.fields','Cabin', ondelete='cascade', domain="['&',('ttype', '=', 'many2one'),('model_id','=',res_model_id)]",
        help="Selected field data willbe shown on cabin column in waiting screen.")
    acs_state_field_id = fields.Many2one('ir.model.fields','State', ondelete='cascade', domain="['&',('ttype', '=', 'selection'),('model_id','=',res_model_id)]", required=True,
        help="On Selected field domain will be appliend on record to be shown in waiting screen.")
    acs_states_to_include = fields.Char(string="Records with States to Include in WC", default="['waiting','in_consultation']",
        help="Enter State names in proper format and record in those state will be shown in waiting screen.")
    acs_youtube_video_url = fields.Char(string="YouTube Video URL")
    acs_show_video = fields.Boolean(string="Show Video")
    acs_show_date_time = fields.Boolean(string="Show Date & Time")
    acs_access_token = fields.Char(string="Access Token", readonly=True, copy=False, index=True)
    acs_screen_url = fields.Char("Screen URL", compute="_compute_screen_url", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('acs_access_token'):
                vals['acs_access_token'] = secrets.token_urlsafe(16)
        return super().create(vals_list)

    def reset_access_token(self):
        for record in self:
            record.acs_access_token = secrets.token_urlsafe(16)

    @api.onchange('res_model_id')
    def on_change_object(self):
        IMFObj = self.env['ir.model.fields']
        if self.res_model_id:
            
            self.acs_physician_field_id = self.acs_patient_field_id = self.acs_cabin_field_id = self.acs_state_field_id = None
            self.acs_states_to_include = '[]'

            physician_field = IMFObj.search([("model","=",self.res_model_id.model),("name","=","physician_id")], limit=1)
            if physician_field:
                self.acs_physician_field_id = physician_field.id

            patient_field = IMFObj.search([("model","=",self.res_model_id.model),("name","=","patient_id")], limit=1)
            if patient_field:
                self.acs_patient_field_id = patient_field.id

            cabin_field = IMFObj.search([("model","=",self.res_model_id.model),("name","=","cabin_id")], limit=1)
            if cabin_field:
                self.acs_cabin_field_id = cabin_field.id
            else:
                self.show_cabin = False

            state_field = IMFObj.search([("model","=",self.res_model_id.model),("name","=","state")], limit=1)
            if state_field:
                self.acs_state_field_id = state_field.id

            if self.res_model_id.model=='hms.appointment':
                self.acs_states_to_include = "['waiting','in_consultation']"
            if self.res_model_id.model=='acs.laboratory.request':
                self.acs_states_to_include = "['draft','requested']"
            if self.res_model_id.model in ['acs.laboratory.request','acs.patient.laboratory.sample']:
                self.acs_states_to_include = "['draft']"

    def acs_open_website_url(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/almightycs/waitingscreen/{self.acs_access_token}',
            'target': 'new',
        }

    @api.depends('acs_access_token')
    def _compute_screen_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.acs_access_token:
                record.acs_screen_url = f"{base_url}/almightycs/waitingscreen/{record.acs_access_token}"
            else:
                record.acs_screen_url = ""


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: