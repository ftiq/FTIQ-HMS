# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
import base64

class HMSPortal(CustomerPortal):

    #User Profile image update
    def _create_or_update_address(
        self,
        partner_sudo,
        address_type='billing',
        use_delivery_as_billing=False,
        callback='/my/addresses',
        required_fields=False,
        verify_address_values=True,
        **form_data
    ):
        # call the parent method first
        partner_sudo, result = super()._create_or_update_address(
            partner_sudo,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            required_fields=required_fields,
            verify_address_values=verify_address_values,
            **form_data
        )

        # ✅ If an image was sent in the form, update the partner
        if form_data.get('image_1920') and partner_sudo:
            partner_sudo.sudo().write({
                'image_1920': base64.b64encode(form_data.get('image_1920').read())
            })

        return partner_sudo, result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: