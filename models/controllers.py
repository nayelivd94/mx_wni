# -*- coding: utf-8 -*-
from openerp import http

# class MxWni(http.Controller):
#     @http.route('/mx_wni/mx_wni/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mx_wni/mx_wni/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mx_wni.listing', {
#             'root': '/mx_wni/mx_wni',
#             'objects': http.request.env['mx_wni.mx_wni'].search([]),
#         })

#     @http.route('/mx_wni/mx_wni/objects/<model("mx_wni.mx_wni"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mx_wni.object', {
#             'object': obj
#         })