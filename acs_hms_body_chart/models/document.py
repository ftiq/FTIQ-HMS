# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class AcsIrAttachment(models.AbstractModel):
    _inherit = "ir.attachment"

    def acs_get_action(self):
        acs_action_id = self.env.ref('base.action_attachment')
        for rec in self:
            rec.acs_action_id = acs_action_id

    acs_action_id = fields.Integer(compute="acs_get_action")

    def get_default_chart_image(self, department=False, company=False, gender=False):
        chart_image = False
        chart_name = ''
        user_company = self.env.user.sudo().company_id
        if department and gender and gender=='male' and department.acs_default_male_chart_image:
            chart_image = department.acs_default_male_chart_image
            chart_name = department.acs_default_male_chart_image_name
        elif department and gender and gender=='female' and department.acs_default_female_chart_image:
            chart_image = department.acs_default_female_chart_image
            chart_name = department.acs_default_female_chart_image_name
        elif department and department.acs_default_chart_image:
            chart_image = department.acs_default_chart_image
            chart_name = department.acs_default_chart_image_name

        elif company and gender and gender=='male' and company.acs_default_male_chart_image:
            chart_image = company.acs_default_male_chart_image
            chart_name = company.acs_default_male_chart_image_name
        elif company and gender and gender=='female' and company.acs_default_female_chart_image:
            chart_image = company.acs_default_female_chart_image
            chart_name = company.acs_default_female_chart_image_name
        elif company and company.acs_default_chart_image:
            chart_image = company.acs_default_chart_image
            chart_name = company.acs_default_chart_image_name

        elif user_company and gender and gender=='male' and user_company.acs_default_male_chart_image:
            chart_image = user_company.acs_default_male_chart_image
            chart_name = user_company.acs_default_male_chart_image_name
        elif user_company and gender and gender=='female' and user_company.acs_default_female_chart_image:
            chart_image = user_company.acs_default_female_chart_image
            chart_name = user_company.acs_default_female_chart_image_name
        elif user_company.acs_default_chart_image:
            chart_image = user_company.acs_default_chart_image
            chart_name = user_company.acs_default_chart_image_name

        if not chart_image:
            raise UserError(_("No default Chart Image is configured yet. Please Configure it on relevant Department on General Setting."))

        return chart_image,chart_name

    def acs_hms_image_chart(self, param=''):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/my/acs/image/editor/%s%s' % (self.id, param),
        }

    def acs_create_chart_image(self, datas, name, res_model, res_id):
        attachment = self.create({
            'name': name,
            'datas': datas,
            'res_model': res_model,
            'res_id': res_id,
        })
        return attachment

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: