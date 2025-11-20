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
    'name' : 'Invoice Summary Report By AlmightyCS',
    'summary': 'Invoice Summary Report By AlmightyCS',
    'version': '1.0.1',
    'category': 'Accounting',
    'depends' : ['account'],
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'website': 'http://www.almightycs.com',
    'live_test_url': 'https://youtu.be/Jwce5GjoGgk',
    'license': 'OPL-1',
    'description': """Invoice Summary Report By AlmightyCS""",
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/account_view.xml',
        'views/invoice_summary_view.xml',
        'reports/report_invoice_summary.xml',
        'reports/account_invoice_summary_report.xml',
    ],
    'images': [
        'static/description/acs_hms_insurance_almightycs_cover.png',
    ],
    'installable': True,
    'application': False,
    'sequence': 2,
    'price': 51,
    'currency': 'USD',

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: