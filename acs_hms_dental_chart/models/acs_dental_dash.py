# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.tools import format_datetime as tool_format_datetime
from odoo.fields import Command

import json
import logging
_logger = logging.getLogger(__name__)

class AcsHmsDental(models.Model):
    _name = "acs.hms.dental.dash"
    _description = "ACS HMS Dental Chart Dashboard"

    @api.model
    def acs_get_dental_color(self):
        return {"acs_dental_color": self.env.user.acs_dental_color or '#985184'}
    
    @api.model
    def acs_get_company_user(self):
        company = self.env.company
        user = self.env.user
        data = {
            'company_id': company.id,
            'company_name': company.name,
            'company_logo': company.logo,
            'user_id': user.id,
            'user_name': user.name,
        }
        return data

    @api.model
    def acs_get_tooth(self, domain={}):
        Tooth = self.env['acs.hms.tooth'].sudo()

        def acs_serialize(records):
            return [
                {
                    "id": rec.id,
                    "name": rec.name,
                    "number": rec.number,
                    "fdi_code": rec.fdi_code,
                    "quadrant": rec.quadrant,
                    "image": rec.image,
                    "unique_key": f"{rec.id}-{rec.number}-{rec.quadrant}",
                }
                for rec in records
            ]

        base_domain = []
        if domain.get("age_group"):
            if domain.get('age_group') == 'child':
                base_domain += [('is_child_tooth','=',True)]
            if domain.get('age_group') == 'teen':
                base_domain += [('is_teen_tooth','=',True)]
            if domain.get('age_group') == 'adult':
                base_domain += [('is_adult_tooth','=',True)]

        data = {}
        quadrants = ["upper_right", "upper_left", "lower_right", "lower_left"]
        if domain.get("quadrant") and domain["quadrant"] != "all":
            quadrant = domain["quadrant"]
            data[quadrant] = acs_serialize(Tooth.search(base_domain + [("quadrant", "=", quadrant)]))
        else:
            for quadrant in quadrants:
                data[quadrant] = acs_serialize(Tooth.search(base_domain + [("quadrant", "=", quadrant)]))
        return data
    
    @api.model
    def acs_get_surfaces(self):
        Surfaces = self.env['acs.tooth.surface'].sudo().search([])
        data = []
        for srf in Surfaces:
            data.append({
                "id": srf.id,   #add this unique id
                "name": srf.name,
                "selected": False,
            })
        return data
    
    @api.model
    def acs_get_procedures(self):
        Products = self.env['product.product'].sudo().search([('hospital_product_type','=','dental_procedure')])
        data = []
        for prd in Products:
            data.append({
                "id": prd.id,   #add this unique id
                'name': prd.name,
                'image_1920': prd.image_1920,
                'list_price': prd.list_price,
                'currency': self.env.user.sudo().company_id.currency_id.symbol,
                'selected': False,
            })
        return data
    
    @api.model
    def acs_get_procedures_table(self, patient_id, offset=0, limit=20):
        new_procedures = []
        procedures_done = []
        data = {}

        if not patient_id:
            return data
        
        try:
            patient_id = int(patient_id)
        except (ValueError, TypeError):
            return data

        patient = self.env['hms.patient'].browse(patient_id)
        if not patient.exists():
            return data

        patient_new_procedures = patient.patient_procedure_ids.filtered(
            lambda t: (t.department_id.department_type=='dental' or t.tooth_ids) \
                and ((t.state in ['scheduled','running']) or not t.invoice_id) and t.state!='done')
        
        for procedure in patient_new_procedures[offset:offset+limit]:
            procedure = procedure.sudo()
            procedure_date = tool_format_datetime(self.env, procedure.date, dt_format=False)
            new_procedures.append({
                'id': procedure.id,
                'name': procedure.name,
                'tooths': ', '.join([t.name for t in procedure.tooth_ids]) or '',
                'tooth_surfaces': ', '.join([s.name for s in procedure.tooth_surface_ids]) or '',
                'procedure': procedure.product_id.name or '',
                'price_unit': procedure.product_id.lst_price or '',
                'physician': procedure.physician_id.name or '',
                'physician_image': procedure.physician_id.image_1920 or '',
                'date': procedure_date or '',
                'notes': procedure.notes or '',
                'attachments': procedure.attachment_ids.ids,
                'document_preview_url': procedure.document_preview_url,
                'invoice': procedure.invoice_id.id,
                'state': dict(procedure._fields['state'].selection).get(procedure.state),
                'currency': self.env.user.sudo().company_id.currency_id.symbol,
            })

        data['new_procedures'] = new_procedures

        patient_procedures_done = patient.patient_procedure_ids.filtered(
            lambda t: (t.department_id.department_type=='dental' or t.tooth_ids) \
                and t.state in ['done'])
        
        for procedure in patient_procedures_done[offset:offset+limit]:
            procedure = procedure.sudo()
            procedure_date = tool_format_datetime(self.env, procedure.date, dt_format=False)
            procedures_done.append({
                'id': procedure.id,
                'name': procedure.name,
                'tooths': ', '.join([t.name for t in procedure.tooth_ids]) or '',
                'tooth_surfaces': ', '.join([s.name for s in procedure.tooth_surface_ids]) or '',
                'procedure': procedure.product_id.name or '',
                'price_unit': procedure.product_id.lst_price or '',
                'physician': procedure.physician_id.name or '',
                'physician_image': procedure.physician_id.image_1920 or '',
                'date': procedure_date or '',
                'notes': procedure.notes or '',
                'attachments': procedure.attachment_ids,
                'invoice': procedure.invoice_id.id,
                'document_preview_url': procedure.document_preview_url,
                'state': dict(procedure._fields['state'].selection).get(procedure.state),
                'currency': self.env.user.sudo().company_id.currency_id.symbol,
            })
        data['procedures_done'] = procedures_done
        return data
    
    @api.model
    def acs_update_procedure_note(self, procedure_id, note=None):
        if not procedure_id:
            return {'success': False, 'error': 'No procedure id'}

        dental_procedure = self.env['acs.patient.procedure'].browse(procedure_id)
        if dental_procedure.exists():
            dental_procedure.write({'notes': note or ''})
            return {'success': True}
        return {'success': False, 'error': 'Procedure not found'}
 
    @api.model
    def acs_create_dental_procedure(self, patient_id, tooth_ids, surface_ids, 
                                    procedure_id, is_cleaning, is_removing, resModel=None, resId=None):
        
        # _logger.info("\n\n Patient Id ----- %s", patient_id)
        # _logger.info("\n\n Tooth Ids ----- %s", tooth_ids)
        # _logger.info("\n\n Surface Ids ----- %s", surface_ids)
        # _logger.info("\n\n Procedure Id ----- %s", procedure_id)
        # _logger.info("\n\n Active Model ----- %s", resModel)
        # _logger.info("\n\n Active Id ----- %s", resId)
        # _logger.info("\n\n Is Cleaning ----- %s", is_cleaning)
        # _logger.info("\n\n Is Removing ----- %s", is_removing)

        if not patient_id and not procedure_id:
            return {"success": False, "error": "Missing required fields"}

        if not is_cleaning and not is_removing:
            if not tooth_ids and not surface_ids:
                return {"success": False, "error": "Missing required fields"}

        elif is_removing:
            if not tooth_ids:
                return {"success": False, "error": "Missing required fields"}

        patient = self.env['hms.patient'].browse(patient_id)
        procedure = self.env['product.product'].browse(procedure_id)
        tooths = self.env['acs.hms.tooth'].browse(tooth_ids)
        surfaces = self.env['acs.tooth.surface'].browse(surface_ids)

        if not patient.exists() and not procedure.exists():
            return {"success": False, "error": "Invalid records selected"}
            
        if not is_cleaning and is_removing:
            if not tooths or surfaces:
                return {"success": False, "error": "Invalid records selected"}
                
        if is_removing:
            if not tooths:
                return {"success": False, "error": "Invalid records selected"}

        department = self.env['hr.department'].sudo().search([
            ('department_type','=','dental'), ('patient_department','=',True)
        ], limit=1)
        if department:
            department = department.id

        user = self.env.user
        dental_procedure = {
            'patient_id': patient.id,
            'physician_id': user.physician_id.id if user and user.physician_id else False,
            'date': fields.Datetime.now(),
            'tooth_ids': [Command.set(tooths.ids)],
            'tooth_surface_ids': [Command.set(surfaces.ids)],
            'product_id': procedure.id,
            'state': 'scheduled',
            'department_id': department if department else False,
            'price_unit': procedure.lst_price if procedure.lst_price else 1.0,
        }

        if resModel == 'hms.appointment':
            if resId:
                dental_procedure.update({'appointment_ids': [Command.set( [resId])]})
        elif resModel == 'hms.treatment':
            if not resId:
                treatment = patient.treatment_ids.filtered(
                    lambda t: t.department_id.department_type == 'dental' and t.state == 'running')
                if treatment:
                    dental_procedure.update({'treatment_id': treatment[0].id})
            else:
                dental_procedure.update({'treatment_id': resId})
        
        procedure = self.env['acs.patient.procedure'].sudo().create(dental_procedure)
        data = {
            "success": True, 
            "procedure_id": procedure.id, 
            "procedure_name": procedure.name
        }
        return data

    @api.model
    def acs_update_procedure_status(self, procedure_id, state):
        procedure = self.env['acs.patient.procedure'].browse(procedure_id)
        if not procedure.exists():
            return {"success": False, "error": "Dental procedure doesn't exist, please check it."}

        proc_id = procedure.id
        proc_name = procedure.name
        
        if state == 'invoice' and not procedure.invoice_id:
            procedure.action_create_invoice()
        elif state == 'delete' and procedure.state in ['scheduled', 'cancel']:
            procedure.unlink()
            return {
                'success': True,
                'procedure_id': proc_id,
                'procedure_name': proc_name,
                'deleted': True
            }
        elif state == 'running' and procedure.state == 'scheduled':
            procedure.action_running()
        elif state == 'done' and procedure.state == 'running':
            procedure.action_done()
        elif state == 'cancelled' and procedure.state in ['scheduled','running']:
            procedure.action_cancel()

        data = {
            'success': True,
            'procedure_id': procedure.id,
            'procedure_name': procedure.name
        }
        return data
