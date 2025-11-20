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
# Lot blocking related logic reference is taken from OCA module of v8
{
    'name': 'Pharmacy Management',
    'summary': 'Pharmacy Management system. Manage pharmacy operations of sale, purchase, batch pricing and barcoding',
    'description': """Pharmacy Management system. Manage pharmacy operations of sale, purchase, batch pricing and barcoding Pharmacy Menus. Barcode generation
        Batch Wise Pricing Product Expiry Product Manufacture Lock Lot acs hms medical healthcare health care
    """,
    'version': '1.0.2',
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': ['purchase','acs_hms_base', 'acs_product_barcode_generator', 'invoice_with_stock_move', 'invoice_barcode'],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/email_template.xml",
        "views/stock_view.xml",
        "views/product_view.xml",
        "views/invoice_view.xml",
        "report/lot_barcode_report.xml",
        "report/picking_barcode_report.xml",
        "report/paper_format.xml",
        "report/report_invoice.xml",
        "report/medicine_expiry_report.xml",
        "wizard/stock_wizard.xml",
        "wizard/wiz_lock_lot_view.xml",
        "wizard/wiz_medicine_expiry_view.xml",
        "views/menu_item.xml",
    ],
    'images': [
        'static/description/hms_pharmacy_almightycs_odoo_cover.png',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 51,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: