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
    'name': 'Hospitalization - Laboratory Management',
    'summary': 'Manage Lab requests, Lab tests on Hospitalization.',
    'description': """
        This module add functionality to manage Laboratory flow. laboratory management system
        Hospital Management lab tests laboratory invoices laboratory test results ACS HMS
        Hospitalization laboratory management
    """,
    'version': '1.0.3',
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'live_test_url': 'https://youtu.be/IV1-4JgdcuA',
    'license': 'OPL-1',
    'depends': ['acs_hms_hospitalization','acs_hms_laboratory'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/report_acs_lab_prescription.xml',
        'report/discharge_summary_report.xml',

        'views/hms_base_view.xml',
        'views/laboratory_view.xml',
    ],
    'images': [
        'static/description/hms_laboratory_almightycs_cover.png',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 16,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: