# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.
#╔══════════════════════════════════════════════════════════════════╗
#║                                                                  ║
#║                ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                 ║
#║                ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                 ║
#║                ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                 ║
#║                ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                 ║
#║                ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                 ║
#║                ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                 ║
#║                          ╔═╝║     ╔═╝║                           ║
#║                          ╚══╝     ╚══╝                           ║
#║ SOFTWARE DEVELOPED AND SUPPORTED BY ALMIGHTY CONSULTING SERVICES ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   http://www.almightycs.com                      ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
{
    'name': 'Hospital Nursing Operations',
    'version': '1.0.4',
    'summary': 'System for managing Hospital Nursing Operations like Hospitalization Ward Round & Evaluations.',
    'description': """
        System for managing Hospital Nursing Operations like Hospitalization Ward Round & Evaluations.
        This Module Helps You To Manage Your Hospital Ward Rounds medical acs hms almightycs""",
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': ['acs_hms','acs_hms_hospitalization'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'report/report_medication.xml',
        'wizard/medication_plan_view.xml',
        'wizard/medication_report_view.xml',
        'views/acs_hms_nursing.xml',
        'views/acs_hms_medication.xml',
        'views/hms_base.xml',
        'views/menu_item.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'acs_hms_nursing/static/src/views/calendar/**/*',
        ]
    },
    'images': [
        'static/description/acs_hms_nursing_almightycs_cover.png',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 91,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: