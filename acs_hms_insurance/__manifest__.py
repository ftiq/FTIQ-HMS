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
    'name': 'Patient Insurance Management System',
    'summary': 'Patient Insurance Management for Hospital Appointment related Claims',
    'description': """
        Patient Insurance Management for Appointment and related Claims. Hospital Management with Insurance Claim. ACS HMS
    """,
    'category': 'Medical',
    'version': '1.0.2',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': ['acs_hms', 'acs_document_base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        
        'report/report_header_section.xml',
        'report/claim_report.xml',
        'report/claim_sheet_report.xml',
        'report/insurance_pre_approval_report.xml',
        'report/invoice_report.xml',

        'data/email_template.xml',
        'data/data.xml',

        'views/hms_base_view.xml',
        'views/tpa_view.xml',
        'views/insurance_base_view.xml',
        'views/insurance_policy_view.xml',
        'views/insurance_pre_approval_view.xml',
        'views/claim_view.xml', 
        'views/portal_template.xml',
        'views/claim_sheet_view.xml',
        'views/res_config_view.xml',
        'views/menu_items.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'acs_hms_insurance/static/src/scss/custom.scss',
        ]
    },
    'images': [
        'static/description/hms_insuranceacs_almightycs_odoo_cover.png',
    ],
    'installable': True,
    'application': True,
    'sequence': 2,
    'price': 51,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: