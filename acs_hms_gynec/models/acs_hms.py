# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from lxml import etree

class ACSAppointment(models.Model):
    _inherit = 'hms.appointment'

    lmp = fields.Date(string='LMP', help="Last Menstrual Period")
    examination_ids = fields.One2many('systemic.examination', 'appointment_id',string='Examinations')
    rs = fields.Text(string='R.S.', help="Describe about respiratory syncytial virus.")
    cvs = fields.Text(string='CVS.', 
        help="Describe about Chorionic villus sampling. : biopsy of a villus of the chorion at usually 10 to 12 weeks of gestation to obtain fetal cells for the prenatal diagnosis of chromosomal abnormalities.")
    cns = fields.Text(string='CNS', 
        help="Describe about Central Nerve System malformations. Neural tube defects are the most frequent CNS malformations")
    external_genitals = fields.Text(string='External Genitals', help="The external genitalia include the labia majora, mons pubis, labia minora, clitoris, and glands within the vestibule")
    back_spine = fields.Text(string='Back Spine', help="Describe about Back Spine of fetus")
    peripheral_pulsation = fields.Text(string='Peripheral Pulsation', help="Measuring Pulse pressure")

    sonography_obstetric_ids = fields.One2many('hms.appointment.sonography.obstetric', 'appointment_id',string='Sonography Obstetric Reports')
    sonography_pelvis_ids = fields.One2many('hms.appointment.sonography.pelvis', 'appointment_id',string='Sonography Pelvis Reports')
    sonography_follical_ids = fields.One2many('hms.appointment.sonography.follical', 'appointment_id',string='Follicular Sonography Reports')

    gender = fields.Selection(related="patient_id.gender", string='Gender', readonly=True)
    hb = fields.Float(related="evaluation_id.hb", string='HB', help="Hemoglobin count")
    acs_hb_name = fields.Char(related="evaluation_id.acs_hb_name", string='Patient Hemoglobin unit of measure label')
    urine = fields.Char(related="evaluation_id.urine", string='Urine')
    acs_urine_name = fields.Char(related="evaluation_id.acs_urine_name", string='Patient Urine unit of measure label')
    screatinine = fields.Float(related="evaluation_id.screatinine", string='S Creatinine', help='Serum creatinine (a blood measurement) is an important indicator of renal(kidney) health')
    acs_screatinine_name = fields.Char(related="evaluation_id.acs_screatinine_name", string='Patient S Creatinine unit of measure label')
    mammography_history_ids = fields.One2many('hms.patient.mammography_history', 'appointment_id', string='Mammography History')
    pap_history_ids = fields.One2many('hms.patient.pap_history', 'appointment_id', string='PAP smear History')
    colposcopy_history_ids = fields.One2many('hms.patient.colposcopy_history', 'appointment_id', string='Colposcopy History')
    pregnancy_history_ids = fields.One2many('hms.patient.pregnancy', related="patient_id.pregnancy_history_ids", string='Pregnancy History', readonly=False)
    menstrual_history_ids = fields.One2many('hms.patient.menstrual_history', related="patient_id.menstrual_history_ids", string='Menstrual History', readonly=False)
    currently_pregnant = fields.Boolean(related="patient_id.currently_pregnant", string ='Currently Pregnant', readonly=False)
    menopause = fields.Integer(related="patient_id.menopause", string ='Menopause age', readonly=False)
    urinary_problem = fields.Boolean(related="patient_id.urinary_problem", string='Urinary Problem', readonly=False)
    menarche = fields.Integer(related="patient_id.menarche", string ='Menarche age', help="First occurrence of menstruation.", readonly=False)
    contraception_method = fields.Selection([
        ('oral', 'Oral'),
        ('injection', 'Injection'),
        ('subdermic', 'Subdermic'),
        ('dui', 'DUI'),
        ('preservative', 'Preservative'),
        ('tl_done', 'TL/Done'),
        ], string='Contraception Method', related="patient_id.contraception_method", readonly=False)
    contraception_product = fields.Char(related="patient_id.contraception_product", string='Contraception Product', readonly=False)
    dispareunia = fields.Selection([('deep','Deep'),('superficial','Superficial')],"Dyspareunia", help="Difficult or painful sexual intercourse.", related="patient_id.dispareunia", readonly=False)
    gravida = fields.Integer(related="patient_id.gravida", string='Gravida', help="Number of pregnancies", readonly=False)
    premature = fields.Integer(related="patient_id.premature", string='Premature', help="Premature Deliveries", readonly=False)
    abortions = fields.Integer(related="patient_id.abortions", string='Abortions', help='Number of Abortions', readonly=False)
    stillbirths = fields.Integer(related="patient_id.stillbirths", string='Stillbirths', help='No of births of an infant that has died in the womb', readonly=False)
    ectopic = fields.Integer(related="patient_id.ectopic", string='Ectopic', help='An ectopic pregnancy occurs when a fertilized egg implants and grows outside the main cavity of the uterus.', readonly=False)
    vaginal_birth = fields.Integer(related="patient_id.vaginal_birth", string='Vaginal Birth', readonly=False)
    cesarean_birth = fields.Integer(related="patient_id.cesarean_birth", string='Cesarean Birth', readonly=False)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(ACSAppointment, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        context = self.env.context
        if context.get('acs_department_type')=='gynec':
            doc = etree.XML(result['arch'])
            node = doc.xpath("//field[@name='patient_id']")[0]
            node.set('domain', "[('gender','=','female')]")
            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result


class ACSPatient (models.Model):
    _inherit = "hms.patient"

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        for rec in self:
            rec.child_birth_count = len(rec.child_birth_ids)
            rec.pregnancy_birth_count = len(rec.pregnancy_history_ids)

    child_birth_ids = fields.One2many('acs.child.birth', 'patient_id',string='Child Birth')
    child_birth_count = fields.Integer(compute='_rec_count', string='# Child Birth')
    sonography_obstetric_ids = fields.One2many('hms.appointment.sonography.obstetric', 'patient_id',string='Sonography Obstetric Reports')
    sonography_pelvis_ids = fields.One2many('hms.appointment.sonography.pelvis', 'patient_id',string='Sonography Pelvis Reports')
    sonography_follical_ids = fields.One2many('hms.appointment.sonography.follical', 'patient_id',string='Follicular Sonography Reports')

    delivery_ids = fields.One2many('acs.child.birth', 'patient_id',string='Delivery')

    screatinine = fields.Float('S Creatinine',related="last_evaluation_id.screatinine", help='Serum creatinine (a blood measurement) is an important indicator of renal(kidney) health')
    currently_pregnant = fields.Boolean(string ='Currently Pregnant')
    menarche = fields.Integer(string ='Menarche age', help="First occurrence of menstruation.")
    menopause = fields.Integer(string ='Menopause age', help="End of a woman's fertility")
    dispareunia = fields.Selection([('deep','Deep'),('superficial','Superficial')],"Dyspareunia", help="Difficult or painful sexual intercourse.")
    gravida = fields.Integer(string='Gravida', help="Number of pregnancies")
    premature = fields.Integer(string='Premature', help="Premature Deliveries")
    abortions = fields.Integer(string='Abortions', help='Number of Abortions')
    stillbirths = fields.Integer(string='Stillbirths', help='No of births of an infant that has died in the womb')
    ectopic = fields.Integer(string='Ectopic', help='An ectopic pregnancy occurs when a fertilized egg implants and grows outside the main cavity of the uterus.')
    vaginal_birth = fields.Integer(string='Vaginal Birth')
    cesarean_birth = fields.Integer(string='Cesarean Birth')

    menstrual_history_ids = fields.One2many('hms.patient.menstrual_history', 'patient_id', string = 'Menstrual History')
    pregnancy_history_ids = fields.One2many('hms.patient.pregnancy', 'patient_id', string='Pregnancies')
    pregnancy_birth_count = fields.Integer(compute='_rec_count', string='# Pregnancies')
    prenatal_evaluation_ids = fields.One2many('hms.patient.prenatal.evaluation', 'patient_id', string='Prenatal Evaluations')
    mammography = fields.Boolean(string='Mammography', help="Check if the patient does periodic mammographys")
    mammography_last = fields.Date(string='Last mammography', help="Enter the date of the last mammography")
    breast_self_examination = fields.Boolean(string='Breast self-examination', help="Check if patient does and knows how to self examine her breasts")
    pap_test = fields.Boolean(string='PAP test',  help="Check if patient does periodic cytologic pelvic smear screening")
    pap_test_last = fields.Date(string='Last PAP test', help="Enter the date of the last Papanicolau test")
    colposcopy = fields.Boolean(string='Colposcopy', help="Check if the patient has done a colposcopy exam")
    colposcopy_last = fields.Date(string='Last colposcopy', help="Enter the date of the last colposcopy")
    full_term = fields.Integer(string='Full Term', help="Full term pregnancies")
    mammography_history_ids = fields.One2many('hms.patient.mammography_history', 'patient_id', string='Mammography History')
    pap_history_ids = fields.One2many('hms.patient.pap_history', 'patient_id', string='PAP smear History')
    colposcopy_history_ids = fields.One2many('hms.patient.colposcopy_history', 'patient_id', string='Colposcopy History')

    #For Basic Medical Info
    hb = fields.Float(related="last_evaluation_id.hb", string='HB', help="Hemoglobin count")
    urine = fields.Char('Urine', related="last_evaluation_id.urine")
    acs_hb_name = fields.Char(related="last_evaluation_id.acs_hb_name", string='Patient Hemoglobin unit of measure label')
    acs_urine_name = fields.Char(related="last_evaluation_id.acs_urine_name", string='Patient Urine unit of measure label')
    acs_screatinine_name = fields.Char(related="last_evaluation_id.acs_screatinine_name", string='Patient S Creatinine unit of measure label')
    hiv = fields.Selection([('negative','Negative'),('positive','Positive')],"HIV", help="Human immunodeficiency virus that attacks the body's immune system.")
    hbsag = fields.Selection([('negative','Negative'),('positive','Positive')],"HBSAG", help="It is the surface antigen of the hepatitis B virus (HBV) which indicates current hepatitis B infection.")
    sonography_pelvis_ids = fields.One2many('hms.appointment.sonography.pelvis', 'patient_id', string='Sonography Pelvis Reports')
    sonography_follical_ids = fields.One2many('hms.appointment.sonography.follical', 'patient_id', string='Sonography Follical Reports')
    sonography_obstetric_ids = fields.One2many('hms.appointment.sonography.obstetric', 'patient_id', string='Sonography Obstetric Reports')
    examination_ids = fields.One2many('systemic.examination', 'patient_id', string='Systemic Examinations')
    
    urinary_problem = fields.Boolean(string='Urinary Problem')
    contraception_method = fields.Selection([
        ('oral', 'Oral'),
        ('injection', 'Injection'),
        ('subdermic', 'Subdermic'),
        ('dui', 'DUI'),
        ('preservative', 'Preservative'),
        ('tl_done', 'TL/Done'),
        ], string='Contraception Method')
    contraception_product = fields.Char(string='Contraception Product')

    #Remove in 14
    tl_done = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='TL/Done', help="Tubal ligation is a permanent voluntary form of birth control (contraception) in which a woman's Fallopian tubes are surgically cut or blocked off to prevent pregnancy.")
    fertile = fields.Boolean(string ='Infertility', help="Check if patient is in fertile age")    
    aml = fields.Char('AML',size=64, help='Acute myelogenous leukemia (AML) is a cancer of the blood and bone marrow ')

    def action_view_patient_delivery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_gynec.hms_action_form_delivery")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action
    
    def action_view_patient_pregnancies(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_gynec.hms_action_pregnancies")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action


class HrDepartment(models.Model): 
    _inherit = "hr.department"

    department_type = fields.Selection(selection_add=[('gynec','Gynecology')])


class ACSInpatientRegistration(models.Model):
    _inherit = "acs.hospitalization"

    delivery_ids = fields.One2many('acs.child.birth', 'hospitalization_id',string='Delivery')

    def action_view_patient_delivery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms_gynec.hms_action_form_delivery")
        action['domain'] = [('hospitalization_id','=',self.id)]
        action['context'] = {'default_hospitalization_id': self.hospitalization_id.id}
        return action
    
class AcsPatientEvaluation(models.Model):
    _inherit = 'acs.patient.evaluation'

    hb = fields.Float(string='HB', help="Hemoglobin count")
    urine = fields.Char('Urine')
    screatinine = fields.Float('S Creatinine', help='Serum creatinine (a blood measurement) is an important indicator of renal(kidney) health')
    acs_hb_name = fields.Char(string='Patient Hemoglobin unit of measure label', compute='acs_compute_uom_name', default=lambda self: self.acs_get_uom_defaults().get('acs_hb_name'))
    acs_urine_name = fields.Char(string='Patient Urine unit of measure label', compute='acs_compute_uom_name', default=lambda self: self.acs_get_uom_defaults().get('acs_urine_name'))
    acs_screatinine_name = fields.Char(string='Patient Screatinine unit of measure label', compute='acs_compute_uom_name', default=lambda self: self.acs_get_uom_defaults().get('acs_screatinine_name'))

    @api.model
    def acs_get_uom_defaults(self):
        defaults = super(AcsPatientEvaluation, self).acs_get_uom_defaults()
        defaults.update({
            'acs_hb_name': self.env['ir.config_parameter'].sudo().get_param('acs_hms_gynec.acs_patient_hb_uom') or 'g/dl',
            'acs_urine_name': self.env['ir.config_parameter'].sudo().get_param('acs_hms_gynec.acs_patient_urine_uom') or '',
            'acs_screatinine_name': self.env['ir.config_parameter'].sudo().get_param('acs_hms_gynec.acs_patient_screatinine_uom') or 'mg/dl',
        })
        return defaults

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: