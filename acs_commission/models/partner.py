# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, SUPERUSER_ID

class ResPartner(models.Model):
    _inherit = "res.partner"

    commission_role_id = fields.Many2one('acs.commission.role', string='Commission Role')
    commission_ids = fields.One2many('acs.commission', 'partner_id', 'Business Commission')
    provide_commission = fields.Boolean('Grant Commission')
    commission_percentage = fields.Float('Percentage')
    commission_rule_ids = fields.One2many("acs.commission.rule", "partner_id", string="Commission Rules")
    commission_target_rule_ids = fields.One2many("acs.commission.target.rule", "partner_id", string="Commission Target Rules")
    target_based_commission = fields.Boolean('Target Based Commission')

    def commission_action(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_commission.acs_commission_action")
        action['domain'] = [('partner_id','=',self.id)]
        action['context'] = {'default_partner_id': self.id, 'search_default_not_invoiced': 1}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: