# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.release import version

import logging
_logger = logging.getLogger(__name__)

class Appointment(models.Model):
    _inherit = 'hms.appointment'

    is_child = fields.Boolean(related="patient_id.is_child", string="Is Child")    
    head_circum = fields.Float(related="evaluation_id.head_circum", string="Head Circumference")
    acs_head_circum_name = fields.Char(related="evaluation_id.acs_head_circum_name", string='Patient Head Circumference unit of measure label')


class AcsPatientEvaluation(models.Model):
    _inherit = 'acs.patient.evaluation'

    @api.depends('patient_id','patient_id.birthday','date')
    def _get_age_months(self):
        for rec in self:
            if rec.patient_id.birthday:
                delta = relativedelta(rec.date, rec.patient_id.birthday)
                rec.age_month = (delta.years*12) + delta.months

    age_month = fields.Float(compute="_get_age_months", string='Age(Months)', store=True)

class ACSPatient (models.Model):
    _inherit = "hms.patient"

    is_child = fields.Boolean("Is Child")
    birth_weight = fields.Float(string='Birth Weight', help="Weight of Child")
    birth_height = fields.Float(string='Birth Height', help="Height of Child")
    birth_head_circum = fields.Float('Birth Head Circumference')

    head_circum = fields.Float(related="last_evaluation_id.head_circum", string="Head Circumference")
    acs_head_circum_name = fields.Char(related="last_evaluation_id.acs_head_circum_name", string='Patient Head Circumference unit of measure label')

    def get_line_graph_datas(self, record_type):
        if record_type=='height':
            rec_name = 'Height'
            child_value = self.birth_height
        if record_type=='weight':
            rec_name = 'Weight'
            child_value = self.birth_weight
        if record_type=='head_circum':
            rec_name = 'Head Circumference'
            child_value = self.birth_head_circum

        normal_data = []
        child_data = []
        normal_record_datas = self.env['acs.growth.chart.data'].search([('record_type','=',record_type)])

        for normal_record_data in normal_record_datas:
            #Value based on gender
            normal_record_data_value = normal_record_data.male_value if self.gender=='male' else normal_record_data.female_value
            normal_data.append({'x': normal_record_data.age, 'y':normal_record_data_value, 'name': 'Normal %s' % rec_name})
            child_record_data = self.env['acs.patient.evaluation'].search([('patient_id','=',self.id), ('age_month','=',int(normal_record_data.age))], limit=1)
            if child_record_data:
                if record_type=='height' and child_record_data.height:
                    child_value = child_record_data.height
                if record_type=='weight' and child_record_data.weight:
                    child_value = child_record_data.weight
                if record_type=='head_circum' and child_record_data.head_circum:
                    child_value = child_record_data.head_circum
            child_data.append({'x': normal_record_data.age, 'y':child_value, 'name': 'Child %s' % rec_name})

        [normal_graph_title, normal_graph_key] = ['Normal %s Growth' % rec_name, _('Normal %s Growth' % rec_name)]
        [child_graph_title, child_graph_key] = ['Child %s Growth' % rec_name, _('Child %s Growth' % rec_name)]

        return [
            {'values': normal_data, 'title': normal_graph_title, 'key': normal_graph_key, 'area': False},
            {'values': child_data, 'title': child_graph_title, 'key': child_graph_key, 'area': False}
        ]

    def acs_get_paediatric_data(self):
        self.ensure_one()
        data = {
            'patient_height_growth': json.dumps(self.get_line_graph_datas('height')),
            'patient_weight_growth': json.dumps(self.get_line_graph_datas('weight')),
            'patient_head_circum_graph': json.dumps(self.get_line_graph_datas('head_circum')),
        }
        _logger.info("\n Paediatric Data ----- %s", data)
        return data
    
    def acs_show_growth_chart(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'AlmightyHmsPaediatric',
            'params': {
                'active_id': self.id,
                'active_model': 'hms.patient',
                'domain': [('id','=',self.id)]
            }
        }

class HrDepartment(models.Model): 
    _inherit = "hr.department"

    department_type = fields.Selection(selection_add=[('paediatric','Paediatric')])

class ACSProduct(models.Model):
    _inherit = 'product.template'

    hospital_product_type = fields.Selection(selection_add=[('paediatric_procedure','Paediatric Process')])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: