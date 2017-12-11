# -*- coding: utf-8 -*-
{
    'name': "mx_wni",

    'summary': """
        Adaptaciones a wni""",

    'description': """
        adaptaciones a wni
    """,

    'author': "Nayeli Valencia Diaz",
    'website': "http://www.xmarts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','purchase','stock'],

    # always loaded
    'data': [
        
        'views/views.xml',
        'views/templates.xml',
        'views/layout.xml',
        'views/report_saleorder.xml',
        'views/report_quotation.xml',
        'views/report_purchase.xml',
        'views/report_purchase.xml',
        'views/report_comision.xml',
        'views/report_service.xml',
        'security/ir.model.access.csv',
        'data/invoice_action_data.xml',
        'data/sale_emaildata.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    
}