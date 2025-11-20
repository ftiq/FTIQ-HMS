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
#║               SOFTWARE DEVELOPED AND SUPPORTED BY                ║
#║          ALMIGHTY CONSULTING SOLUTIONS PRIVATE LIMITED           ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   https://www.almightycs.com                     ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
{
    'name' : 'Patient Invoice Summary Report By AlmightyCS',
    'summary': 'Invoice Summary Report for Patient By AlmightyCS',
    'version': '1.0.1',
    'category' : 'Extra-Addons',
    'depends' : ['acs_hms', 'acs_invoice_summary'],
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'website': 'http://www.almightycs.com',
    'live_test_url': 'https://youtu.be/Jwce5GjoGgk',
    'license': 'OPL-1',
    'description': """Invoice Summary Report for Patient By AlmightyCS""",
    'data': [
        'views/hms_base.xml',
        'reports/report_invoice_summary.xml',
    ],
    'images': [
        'static/description/acs_hms_insurance_almightycs_cover.png',
    ],
    'installable': True,
    'application': False,
    'sequence': 2,
    'price': 10,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: