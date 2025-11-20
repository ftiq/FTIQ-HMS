# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models ,_
from odoo.exceptions import UserError


class ACSFamilyRelation(models.Model):
    _name = 'acs.family.relation'
    _description = "Family Relation"
    _order = "sequence"

    name = fields.Char(required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    inverse_relation_id = fields.Many2one("acs.family.relation", string="Inverse Relation")

    def _compute_display_name(self):
        for rec in self:
            name = rec.name 
            if rec.inverse_relation_id:
                name += ' - ' + rec.inverse_relation_id.name
            rec.display_name = name

    _name_uniq = models.Constraint(
        'unique (name)',
        "The Relation must be unique!",
    )

    def manage_inverse_relation(self):
        for rec in self:
            if rec.inverse_relation_id and not rec.inverse_relation_id.inverse_relation_id:
                rec.inverse_relation_id.inverse_relation_id = rec.id

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.manage_inverse_relation()
        return res

    def write(self, values):
        res = super(ACSFamilyRelation, self).write(values)
        self.manage_inverse_relation()
        return res


class ACSFamilyMember(models.Model):
    _name = 'acs.family.member'
    _description= 'Family Member'

    related_patient_id = fields.Many2one('hms.patient', string='Family Member', help='Family Member Name', required=True)    
    patient_id = fields.Many2one('hms.patient', string='Patient')
    relation_id = fields.Many2one('acs.family.relation', string='Relation', required=True)
    inverse_relation_id = fields.Many2one("acs.family.member", string="Inverse Relation")

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            if not record.inverse_relation_id and record.relation_id.inverse_relation_id:
                inverse_relation_id = self.create({
                    'inverse_relation_id': record.id,
                    'relation_id': record.relation_id.inverse_relation_id.id,
                    'patient_id': record.related_patient_id.id,
                    'related_patient_id': record.patient_id.id,
                })
                record.inverse_relation_id = inverse_relation_id.id
        return res

    def unlink(self):
        inverse_relation_id = self.mapped('inverse_relation_id')
        res = super(ACSFamilyMember, self).unlink()
        if inverse_relation_id:
            inverse_relation_id.unlink()
        return res

    def write(self, values):
        res = super(ACSFamilyMember, self).write(values)
        if 'patient_id' in values or 'related_patient_id' in values :
            raise UserError(_("Please Delete Exiting relation and create new!"))

        if 'relation_id' in values:
            for rec in self:
                if rec.inverse_relation_id and rec.relation_id.inverse_relation_id and rec.relation_id.inverse_relation_id!=rec.inverse_relation_id.relation_id:
                    rec.inverse_relation_id.relation_id = rec.relation_id.inverse_relation_id.id
        return res