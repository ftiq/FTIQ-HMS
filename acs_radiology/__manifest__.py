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
    'name': 'Radiology Management',
    'summary': 'Manage Radiology requests, Radiology tests, Invoicing and related history for hospital.',
    'description': """
        This module add functionality to manage Radiology flow. radiology management system
        Hospital Management Radiology tests radiology invoices radiology test results ACS HMS
    """,
    'version': '1.0.7',
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'live_test_url': 'https://youtu.be/md87kak6ztQ',
    'license': 'OPL-1',
    'depends': ['acs_hms_base', 'acs_documents_preview'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/radiology_prescription.xml',
        'report/radiology_report.xml',
        'report/radiology_request_results.xml',

        'data/mail_template.xml',
        'data/data.xml',
        'data/digest_data.xml',

        'views/radiology_request_view.xml',
        'views/radiology_test_view.xml',
        'views/radiology_patient_test_view.xml',
        'views/hms_base_view.xml',
        'views/res_config.xml',
        'views/portal_template.xml',
        'views/templates_view.xml',
        'views/radiology_view.xml',
        'views/digest_view.xml',

        'views/menu_item.xml',
    ],
    'demo': [
        'data/radiology_demo.xml',
    ],
    'images': [
        'static/description/hms_radiology_almightycs_cover.png',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 61,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: