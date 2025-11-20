# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
#╔══════════════════════════════════════════════════════════════════════╗
#║                                                                      ║
#║                  ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                   ║
#║                  ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                   ║
#║                  ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                   ║
#║                  ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                   ║
#║                  ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                   ║
#║                  ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                   ║
#║                            ╔═╝║     ╔═╝║                             ║
#║                            ╚══╝     ╚══╝                             ║
#║                  SOFTWARE DEVELOPED AND SUPPORTED BY                 ║
#║                ALMIGHTY CONSULTING SOLUTIONS PVT. LTD.               ║
#║                      COPYRIGHT (C) 2016 - TODAY                      ║
#║                      https://www.almightycs.com                      ║
#║                                                                      ║
#╚══════════════════════════════════════════════════════════════════════╝
{
    'name': 'Hospitalization & Surgery - Consent Form Management',
    'summary': """Automatically Manage Electronic Consent Forms for Hospitalization, and Surgeries.""",
    'description': """
        This module automates the creation and management of digital consent forms for patients.
        - Automatically creates an **Electronic Consent Form** when a **Hospitalization**,
          or **Surgery** is created for a patient.
        - Simplifies consent tracking and ensures proper documentation of all patient procedures.
        - Supports digital signatures for seamless and paperless consent management.
    """,

    'version': '1.0.1',
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': ["acs_hms_consent_form","acs_hms_hospitalization","acs_hms_surgery"],
    'data' : [
        'security/ir.model.access.csv',
        'views/hms_hospitalization.xml',
        'views/acs_consent_form.xml',
        'views/hms_surgery_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/odoo_acs_consent_form_almightycs.png',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 26,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
