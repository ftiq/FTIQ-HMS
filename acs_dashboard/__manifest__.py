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
    "name": "Dashboard Base",
    "summary": "Dashboard for users.",
    "description": """Dashboard for users.""", 
    'version': '1.0.1',
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    "depends": ["web"],
    "data": [
        "views/acs_dashboard_view.xml",
        "views/res_user_view.xml",
    ],  
    'assets': {
        'web.assets_backend': [
            'acs_dashboard/static/src/lib/js/core.js',
            'acs_dashboard/static/src/lib/js/charts.js',
            'acs_dashboard/static/src/lib/js/animated.js',
            'acs_dashboard/static/src/components/**/*',
            'acs_dashboard/static/src/css/*.css',
        ],
    },
    'images': [
        'static/description/acs_hms_dashboard_almightycs_odoo_cover.png',
    ],
    'cloc_exclude': [
        "static/src/lib/**/*", # exclude all files in a folder hierarchy recursively
    ],
    'application': False,
    'sequence': 2,
    'price': 75,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: