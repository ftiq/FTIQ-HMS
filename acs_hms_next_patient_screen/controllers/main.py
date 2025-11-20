# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request, Response
from odoo.tools.translate import _
import json


class AcsNextPatientScreen(http.Controller):

    @http.route(['/almightycs/waitingscreen/<string:token>'], type='http', auth="public", website=True, sitemap=False)
    def acs_waiting_screen(self, token=None, **kw):
        screen = request.env['acs.hms.waiting.screen'].sudo().search([('acs_access_token','=',token)])
        if not screen:
            return request.render("acs_hms_next_patient_screen.template_warning_popup")
        ResModel = request.env[screen.res_model_id.model]
        domain = [('company_id','=',screen.company_id.id)]
        if screen and screen.physician_ids and screen.acs_physician_field_id:
            domain += [(screen.acs_physician_field_id.name,'in',screen.physician_ids.ids)]
        if screen.acs_states_to_include and screen.acs_state_field_id:
            domain += [(screen.acs_state_field_id.name, 'in', eval(screen.acs_states_to_include))]
        limit = screen.acs_number_of_records or 5
        records = ResModel.sudo().search(domain, order="id asc", limit=limit)
        return request.render("acs_hms_next_patient_screen.next_patient_view",{'acs_ws': screen, 'records': records, 'ResModel': ResModel})

    @http.route('/almightycs/waitingscreen/data/<string:token>', type='jsonrpc', auth='public', website=True, methods=['POST'])
    def acs_waiting_screen_data(self, token, **kw):
        screen = request.env['acs.hms.waiting.screen'].sudo().search([('acs_access_token','=',token)], limit=1)
        if not screen:
            return {'error': 'Invalid screen token.'}
        company_lang_raw = screen.company_id.partner_id.lang.replace('_', '-')
        ResModel = request.env[screen.res_model_id.model]
        domain = [('company_id', '=', screen.company_id.id)]
        if screen.physician_ids and screen.acs_physician_field_id:
            domain += [(screen.acs_physician_field_id.name, 'in', screen.physician_ids.ids)]
        if screen.acs_states_to_include and screen.acs_state_field_id:
            domain += [(screen.acs_state_field_id.name, 'in', eval(screen.acs_states_to_include))]
        limit = screen.acs_number_of_records or 5
        in_consultation_records = ResModel.sudo().search(domain + [('state', '=', 'in_consultation')], order="id asc")
        remaining_limit = max(0, limit - len(in_consultation_records))
        other_records = ResModel.sudo().search(domain + [('state', '!=', 'in_consultation')], order="id asc", limit=remaining_limit)
        final_records = in_consultation_records + other_records
        records_data = []
        normal_index = 1
        current_states = {}
        for rec in final_records:
            state = rec.state
            current_states[str(rec.id)] = rec.state
            number = 'NOW' if state == 'in_consultation' else str(normal_index)
            if state != 'in_consultation':
                normal_index += 1

            data = {
                'state': number,
                'image': 'data:image/png;base64,' + rec.patient_id.image_1920.decode('utf-8') if rec.patient_id.image_1920 else '',
                'show_image': screen.show_patient_name_image,
                'patient_name': rec.patient_id.name if rec.patient_id else '-------',
                'physician_name': rec.physician_id.name if rec.physician_id else '-------',
                'show_cabin': screen.show_cabin,
                'cabin_name': rec.cabin_id.name if hasattr(rec, 'cabin_id') and rec.cabin_id else '',
                'appointment_number': rec.name or '-------',
                'text_color_class': screen.in_progress_color if state == 'in_consultation' else '',
            }
            records_data.append(data)
        html_content = request.env['ir.ui.view']._render_template('acs_hms_next_patient_screen.template_waiting_screen_html', {'records': records_data, 'company_lang': company_lang_raw})
        return {'html': html_content, 'states': current_states}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: