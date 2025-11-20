# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move','acs.whatsapp.mixin']

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.hospital_invoice_type=='pharmacy' and rec.partner_id.phone:
                company_id = rec.sudo().company_id or rec.env.user.sudo().company_id
                template = company_id.acs_pharmacy_order_template_id
                if rec.partner_id.phone and template:
                    rendered = self.env['mail.render.mixin']._render_template(template.body_message, rec._name, [rec.id])
                    msg = rendered[rec.id]
                    rec.send_whatsapp(msg, rec.partner_id.phone, rec.partner_id, template=template, company_id=company_id.id)
        return res
    
    def acs_send_reminder_msg(self, move, med_name, line):
        move,med_name,line = super(AccountMove, self).acs_send_reminder_msg(move, med_name, line)
        template = self.env.ref("acs_pharmacy_whatsapp.acs_pharmacy_reminder_whatsapp_template",raise_if_not_found=False)
        if template and move.partner_id.phone:
            rendered = move.env['mail.render.mixin']._render_template(template.body_message,move._name,[move.id],add_context={'med_name': med_name})
            msg = rendered[move.id]
            move.send_whatsapp(msg,move.partner_id.phone,move.partner_id,template=template,res_model='account.move',res_id=move.id,company_id=move.company_id.id)
        return move,med_name,line

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: