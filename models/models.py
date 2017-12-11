# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import xlrd
import shutil
import logging
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from datetime import datetime
import operator as py_operator
from odoo.tools.float_utils import float_is_zero, float_compare

_logger = logging.getLogger(__name__)


class OrderPurchaseni(models.Model):
    _inherit = 'purchase.order'

    positondelivery = fields.Selection([
        ('orden', 'Orden de Compra'), ('transito', 'En transito'),
        ('recibida parcial', 'Recibida parcial')],
        'Estatus de Recepción', default='orden', required=False)
    #state = fields.Selection([
    #    ('draft', 'RFQ'),
    #    ('sent', 'RFQ Sent'),
    #    ('to approve', 'To Approve'),
    #    ('purchase', 'Purchase Order'),
    #    ('partially_received', 'Parcialmente recibida'),
    #    ('received', 'Recibida'),
    #    ('partially_invoiced', 'Parcialmente Facturada'),
    #    ('invoiced', 'Facturada'),
    #    ('done', 'Locked'),
    #    ('cancel', 'Cancelled')
    #], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    delivery_id = fields.Many2one('res.partner', string="Entrega en",
                                  domain="['&',('parent_id','=',1),('type', '=', 'delivery')]")
    #partially_invoiced = fields.Boolean(string="parcialmente facturada", default=False)
    #invoiced = fields.Boolean(string="parcialmente facturada", default=False)

    #@api.depends('state', 'order_line.qty_invoiced', 'order_line.product_qty', 'invoiced')
    #def _get_invoiced(self):
    #    precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #    for order in self:
    #        _logger.info(_("entro al for  \n%s") % (order.invoiced))
    #        if order.state == 'purchase' or order.state == 'partially_received' and order.invoiced ==False:
    #            _logger.info(_("entro al if de purchase  \n"))
    #            order.invoice_status = 'to invoice'
    #        if order.invoiced == True:
    #            _logger.info(_("entro al if de no   \n"))
    #            order.invoice_status = 'no'
    #            # if any(float_compare(line.qty_invoiced, line.product_qty, precision_digits=precision) == -1 for line in order.order_line):
                #  order.invoice_status = 'to invoice'
                #  _logger.info(_("TO INVOICE \n"))
                # elif all(float_compare(line.qty_invoiced, line.product_qty, precision_digits=precision) >= 0 for line in order.order_line):
                # order.invoice_status = 'invoiced'
                #  _logger.info(_("INVOICEDE \n"))
                # else:
                #  if order.invoiced == True:
                #    order.invoice_status = 'no'
                #    _logger.info(_("TO no  \n"))

    #@api.depends('picking_ids', 'picking_ids.state', 'state')
   # def _compute_is_shipped(self):
   #     for order in self:
   #         if order.state == 'received':
   #             order.is_shipped = True

#    @api.multi
 #   def button_confirm(self):
 #       for order in self:
  #          order.invoiced = False
   #         if order.state not in ['draft', 'sent']:
   #             continue
   #         order._add_supplier_to_product()
   #         # Deal with double validation process
   #         if order.company_id.po_double_validation == 'one_step':
   #             order.button_approve(force=True)
   #         else:
   #             order.write({'state': 'to approve'})
   #     return True


class StockWni(models.Model):
    _inherit = 'stock.picking'
    wni_pedimento = fields.Char('Pedimento')
    aduana = fields.Char('Aduana')
    wni_datepedimento = fields.Date(string='Fecha Pedimento')
    wni_issale = fields.Boolean(string="is Sale", default=False, readonly=True)


class AccountinvoiceWni(models.Model):
    _inherit = 'account.invoice'
    wni_pedimento = fields.Char('Pedimento')
    aduana = fields.Char('Aduana')
    wni_datepedimento = fields.Date(string='Fecha Pedimento')


class stockpickingwni(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('pack_operation_product_ids')
    def _onchange_origin(self):
        # super(StockPicking, self)._onchange_origin()
        if self.pack_operation_product_ids:
            x = 0
            for line in self.pack_operation_product_ids:
                if x: break
                if line.qty_done > line.product_qty:
                    raise UserError(_("Error: La cantidad recibida debe ser igual a la cantidad por hacer! "))
                x += 1

    @api.one
    def load_series(self):

        attachment_obj = self.env['ir.attachment']
        attachments = []
        company_id = self.company_id.id
        stockpicking = self
        # fname_stockpicking = stockpicking.fname_stockpicking and stockpicking.fname_stockpicking or ''
        adjuntos = attachment_obj.search([('res_model', '=', 'stock.picking'),
                                          ('res_id', '=', stockpicking.id),
                                          ('name', 'like', '%.xls')])
        # raise UserError(_("Error:Hay \n%s!") % (stockpicking.id))
        _logger.error(" archivos ajuntos")
        count = 0
        for attach in adjuntos:
            count += 1

        if count >= 2 or count == 0:
            raise UserError(_(
                "Error:Hay \n%s archivos adjuntos, por favor adjunte el archivo o sólo deje el archivo para cargar sus series!") % (
                            count))
        else:
            if count == 1:
                _logger.error("hay 1 archivo ajuntos")
                db_name = self._cr.dbname
                _logger.info('ERROR LA BD ES: %s' % db_name)
                # destino = "/var/lib/odoo/filestore/" +db_name +"/"  + adjuntos.store_fname+".xls";
                destino = "/var/lib/odoo/.local/share/Odoo/filestore/" + db_name + "/" + adjuntos.store_fname + ".xls";
                shutil.copy('/var/lib/odoo/.local/share/Odoo/filestore/' + db_name + '/' + adjuntos.store_fname,
                            destino)
                # shutil.copy('/var/lib/odoo/filestore/' +db_name +"/"  + adjuntos.store_fname, destino)
                _logger.info("ARCHIVO COPIADO")
                book = xlrd.open_workbook(
                    "/var/lib/odoo/.local/share/Odoo/filestore/" + db_name + "/" + adjuntos.store_fname + ".xls")
                # book = xlrd.open_workbook("/var/lib/odoo/filestore/" +db_name +"/"  + adjuntos.store_fname+".xls")
                # serie_obj = self.pool.get('serie_tmp')
                sheet = book.sheet_by_index(0)

                nrows = sheet.nrows
                ncols = sheet.ncols
                _logger.info(nrows)
                _logger.info(ncols)
                for i in range(nrows):
                    for j in range(ncols):
                        # string += '%st'%sheet.cell_value(i,j)
                        _logger.info(sheet.cell_value(i, 0))
                        _logger.info(sheet.cell_value(i, 1))
                        # if sheet.cell_value(i,4) == '':
                        #   raise UserError(_("Error:vacio columna 5 \n%s!") % ())
                        serie_obj = self.env['serie_tmp']
                        self.write({'xls_file_signed_index': adjuntos.store_fname})
                        serie_vals = {
                            'producto': sheet.cell_value(i, 0),
                            'serie': sheet.cell_value(i, 1),
                            'stockpicking_id': stockpicking.id,
                        }
                    serie_create_id = serie_obj.create(serie_vals)
                    _logger.info("Termino de guardar")

    @api.one
    def cargar_series(self):
        attachment_obj = self.env['ir.attachment']
        attachments = []
        company_id = self.company_id.id
        stockpicking = self
        # fname_stockpicking = stockpicking.fname_stockpicking and stockpicking.fname_stockpicking or ''
        adjuntos = attachment_obj.search([('res_model', '=', 'stock.picking'),
                                          ('res_id', '=', stockpicking.id),
                                          ('name', 'like', '%.xls')])
        # raise UserError(_("Error:Hay \n%s!") % (stockpicking.id))
        _logger.error(" archivos ajuntos")
        count = 0
        for attach in adjuntos:
            count += 1

        if count >= 2 or count == 0:
            raise UserError(_(
                "Error:Hay \n%s archivos adjuntos, por favor adjunte el archivo o sólo deje el archivo para cargar sus series!") % (
                            count))
        else:
            if count == 1:
                _logger.error("hay 1 archivo ajuntos")
                db_name = self._cr.dbname
                # destino = "/var/lib/odoo/filestore/" +db_name +"/"  + adjuntos.store_fname+".xls";
                destino = "/var/lib/odoo/.local/share/Odoo/filestore/" + db_name + "/" + adjuntos.store_fname + ".xls";
                shutil.copy('/var/lib/odoo/.local/share/Odoo/filestore/' + db_name + "/" + adjuntos.store_fname,
                            destino)
                # shutil.copy('/var/lib/odoo/filestore/' +db_name +"/"  + adjuntos.store_fname, destino)
                _logger.info("ARCHIVO COPIADO")
                book = xlrd.open_workbook(
                    "/var/lib/odoo/.local/share/Odoo/filestore/" + db_name + "/" + adjuntos.store_fname + ".xls")
                # book = xlrd.open_workbook("/var/lib/odoo/filestore/" +db_name +"/"  + adjuntos.store_fname+".xls")
                # serie_obj = self.pool.get('serie_tmp')
                sheet = book.sheet_by_index(0)

                nrows = sheet.nrows
                ncols = sheet.ncols
                _logger.info(nrows)
                _logger.info(ncols)
                for i in range(nrows):
                    for j in range(ncols):
                        # string += '%st'%sheet.cell_value(i,j)
                        _logger.info(sheet.cell_value(i, 0))
                        _logger.info(sheet.cell_value(i, 1))
                        # if sheet.cell_value(i,4) == '':
                        #   raise UserError(_("Error:vacio columna 5 \n%s!") % ())
                        serie_obj = self.env['load_series']
                        self.write({'xls_file_signed_index': adjuntos.store_fname})
                        serie_vals = {
                            'producto': sheet.cell_value(i, 0),
                            'serie': sheet.cell_value(i, 1),
                            'stockpicking_id': stockpicking.id,
                        }
                    serie_create_id = serie_obj.create(serie_vals)
                    _logger.info("Termino de guardar")

    @api.one
    def series_aleatoria(self):
        attachment_obj = self.env['ir.attachment']
        attachments = []
        company_id = self.company_id.id
        stockpicking = self

        _logger.error("Entro a cargar aleatoriamente")

        serie_obj = self.env['series_aleatorias']
        serie_vals = {
            'stockpicking_id': stockpicking.id,
        }
        serie_create_id = serie_obj.create(serie_vals)
        _logger.info("Termino de guardar")


class Wnimx_series_temp(models.Model):
    _name = 'serie_tmp'
    producto = fields.Char("producto")
    serie = fields.Char("No. Serie")
    qty = fields.Char("Cantidad")
    start = fields.Text("Almacen de")
    finish = fields.Text("Almacen hasta")
    stockpicking_id = fields.Integer("Stock Picking id")


class mxwnistockproduction(models.Model):
    _inherit = 'stock.production.lot'
    load = fields.Boolean(string="Cargado", default=True)


class Wnimx_load_series(models.Model):
    _name = 'load_series'
    producto = fields.Char("producto")
    serie = fields.Char("No. Serie")
    qty = fields.Char("Cantidad")
    start = fields.Text("Almacen de")
    finish = fields.Text("Almacen hasta")
    stockpicking_id = fields.Integer("Stock Picking id")


class Wnimx_series_aleatoria(models.Model):
    _name = 'series_aleatorias'
    producto = fields.Char("producto")
    serie = fields.Char("No. Serie")
    qty = fields.Char("Cantidad")
    start = fields.Text("Almacen de")
    finish = fields.Text("Almacen hasta")
    stockpicking_id = fields.Integer("Stock Picking id")


class wnimx_salestaus(models.Model):
    _inherit = 'sale.order'
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('pending', 'Pendiente por Validar'),
        ('validada', 'Validada'),
        ('sale', 'Sale Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    # state=fields.Selection(selection_add=[('pending', 'Pendiente')])
    # def pending_validate(self,cr,uid,ids,context=None):
    # res=self.write(cr,uid,ids,{'state':'pending'}, context=context)
    # return res
    @api.multi
    def pending_validate(self):
        attachment_obj = self.env['ir.attachment']
        attachments = []
        saleorder = self
        adjuntos = attachment_obj.search([('res_model', '=', 'sale.order'),
                                          ('res_id', '=', saleorder.id)])

        _logger.info(_("Error:Hay \n%s valor de adjunto") % (adjuntos))

        count = 0
        bol = False
        for attach in adjuntos:
            count += 1
        if bol == False:
            bol = True

        if count == 0 or count == 1:
            raise UserError(_("Error:Tiene que adjuntar un archivo"))
        else:
            if count >= 2:
                _logger.info("hay archivo ajuntos")
                self.write({'state': 'pending'})
                # if bol==False:
                # raise UserError(_("Error:Tiene que adjuntar un archivo"))

    @api.multi
    def validate(self):
        self.write({'state': 'validada'})
        # self.write({'wni_validate': 'True'})
    wni_validate = fields.Boolean(string="Validada", default=False, readonly=True)


class AccountpaymentWni(models.Model):
    _inherit = 'account.payment'
    journal_id = fields.Many2one(string='Cuenta de Ingreso')
    partner_acc_id = fields.Many2one(string='Cuenta de Cliente')
    cmpl_type = fields.Selection([('check', 'Cheque'),
                                  ('transfer', 'Transferencia'),
                                  ('payment', 'Otro método de pago')],
                                 string='Tipo de depósito',
                                 help='Indique el tipo de complemento a usar para este pago.')
# class ReportStockForecatwni(models.Model):
#   _inherit = 'report.stock.forecast'
#  @api.multi
# @api.model_cr
# def init(self):
#        tools.drop_view_if_exists(self._cr, 'report_stock_forecast')
#       self._cr.execute("""CREATE or REPLACE VIEW report_stock_forecast AS (SELECT
#      MIN(id) as id,
#     product_id as product_id,
#     date as date,
#    sum(product_qty) AS quantity,
#   sum(sum(product_qty)) OVER (PARTITION BY product_id ORDER BY date) AS cumulative_quantity
#   FROM
# (SELECT
#  MIN(id) as id,
#  MAIN.product_id as product_id,
# SUB.date as date,
# CASE WHEN MAIN.date = SUB.date THEN sum(MAIN.product_qty) ELSE 0 END as product_qty
# FROM
# (SELECT
#   MIN(sq.id) as id,
# sq.product_id,
# date_trunc('week', to_date(to_char(CURRENT_DATE, 'YYYY/MM/DD'), 'YYYY/MM/DD')) as date,
# SUM(sq.qty) AS product_qty
#           FROM
#           stock_quant as sq
#           LEFT JOIN
#            product_product ON product_product.id = sq.product_id
#            LEFT JOIN
#            stock_location location_id ON sq.location_id = location_id.id
#            WHERE
#            location_id.usage = 'internal'
#            GROUP BY date, sq.product_id
#            UNION ALL
#            SELECT
#            MIN(-sm.id) as id,
#            sm.product_id,
#           CASE WHEN sm.date_expected > CURRENT_DATE
#           THEN date_trunc('week', to_date(to_char(sm.date_expected, 'YYYY/MM/DD'), 'YYYY/MM/DD'))
#          ELSE date_trunc('week', to_date(to_char(CURRENT_DATE, 'YYYY/MM/DD'), 'YYYY/MM/DD')) END
#          AS date,
#         SUM(sm.product_qty) AS product_qty
#           FROM
#            stock_move as sm
#          LEFT JOIN
#        product_product ON product_product.id = sm.product_id
#       LEFT JOIN
#          stock_location dest_location ON sm.location_dest_id = dest_location.id
#           LEFT JOIN
#            stock_location source_location ON sm.location_id = source_location.id
#           WHERE
#          sm.state IN ('confirmed','assigned','waiting') and
#         source_location.usage != 'internal' and dest_location.usage = 'internal'
#           and sm.origin not ilike 'PO%'
#            GROUP BY sm.date_expected,sm.product_id
#           UNION ALL
#          SELECT
#               MIN(-sm.id) as id,
#             sm.product_id,
#   #            CASE WHEN sm.date_expected > CURRENT_DATE
#                   THEN date_trunc('week', to_date(to_char(sm.date_expected, 'YYYY/MM/DD'), 'YYYY/MM/DD'))
#                    ELSE date_trunc('week', to_date(to_char(CURRENT_DATE, 'YYYY/MM/DD'), 'YYYY/MM/DD')) END
#               AS date,
#                SUM(-(sm.product_qty)) AS product_qty
#            FROM
#               stock_move as sm
#            LEFT JOIN
#               product_product ON product_product.id = sm.product_id
#            LEFT JOIN
#               stock_location source_location ON sm.location_id = source_location.id
#          LEFT JOIN
#              stock_location dest_location ON sm.location_dest_id = dest_location.id
#           WHERE
#   #              sm.state IN ('confirmed','assigned','waiting') and
#           source_location.usage = 'internal' and dest_location.usage != 'internal'
#          GROUP BY sm.date_expected,sm.product_id)
#        as MAIN
#     LEFT JOIN
#     (SELECT DISTINCT date
#      FROM
#      (
#             SELECT date_trunc('week', CURRENT_DATE) AS DATE
#             UNION ALL
#             SELECT date_trunc('week', to_date(to_char(sm.date_expected, 'YYYY/MM/DD'), 'YYYY/MM/DD')) AS date
#             FROM stock_move sm
#             LEFT JOIN
#             stock_location source_location ON sm.location_id = source_location.id
#             LEFT JOIN
#             stock_location dest_location ON sm.location_dest_id = dest_location.id
#             WHERE
#             sm.state IN ('confirmed','assigned','waiting') and sm.date_expected > CURRENT_DATE and
#             ((dest_location.usage = 'internal' AND source_location.usage != 'internal')
#              or (source_location.usage = 'internal' AND dest_location.usage != 'internal'))) AS DATE_SEARCH)
#             SUB ON (SUB.date IS NOT NULL)
#    GROUP BY MAIN.product_id,SUB.date, MAIN.date
#    ) AS FINAL
#    GROUP BY product_id,date)""")

# class Productwni(models.Model):
#    _inherit = "product.product"
#
#    @api.multi
#   def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
#       domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
#        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
#        dates_in_the_past = False
#        if to_date and to_date < fields.Datetime.now(): #Only to_date as to_date will correspond to qty_available
#            dates_in_the_past = True
#
#        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
#        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
#        if lot_id:
#            domain_quant += [('lot_id', '=', lot_id)]
#        if owner_id:
#            domain_quant += [('owner_id', '=', owner_id)]
#            domain_move_in += [('restrict_partner_id', '=', owner_id)]
#            domain_move_out += [('restrict_partner_id', '=', owner_id)]
#        if package_id:
#            domain_quant += [('package_id', '=', package_id)]
#        if dates_in_the_past:
#            domain_move_in_done = list(domain_move_in)
#            domain_move_out_done = list(domain_move_out)
#        if from_date:
#            domain_move_in += [('date', '>=', from_date)]
#            domain_move_out += [('date', '>=', from_date)]
#        if to_date:
#            domain_move_in += [('date', '<=', to_date)]
#            domain_move_out += [('date', '<=', to_date)]
#
#         Move = self.env['stock.move']
#         Quant = self.env['stock.quant']
#        domain_move_in_todo = [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_in
#        domain_move_out_todo = [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_out
#        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id']))
#        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id']))
#        quants_res = dict((item['product_id'][0], item['qty']) for item in Quant.read_group(domain_quant, ['product_id', 'qty'], ['product_id']))
#        if dates_in_the_past:
#            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
#            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
#            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
#            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id']))
#            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id']) # #)
#
#        res = dict()
#        for product in self.with_context(prefetch_fields=False):
#            res[product.id] = {}
#            if dates_in_the_past:
#                qty_available = quants_res.get(product.id, 0.0) + moves_out_res_past.get(product.id, 0.0)
#            else:
#                qty_available = quants_res.get(product.id, 0.0)
#           res[product.id]['qty_available'] = float_round(qty_available, precision_rounding=product.uom_id.rounding)
#           res[product.id]['incoming_qty'] = float_round(moves_in_res.get(product.id, 0.0), precision_rounding=product.uom_id.rounding)
#           res[product.id]['outgoing_qty'] = float_round(moves_out_res.get(product.id, 0.0), precision_rounding=product.uom_id.rounding)
#           res[product.id]['virtual_available'] = float_round(


#                qty_available - res[product.id]['outgoing_qty'],
#                precision_rounding=product.uom_id.rounding)
#
#        return res
class StockQuanttWni(models.Model):
  _inherit ='stock.quant'
  categ_id = fields.Many2one('product.category', string="Categoria Interna", store=True)


class StockQuanttWni(models.Model):
    _inherit = 'stock.pack.operation'
    assort = fields.Float(string="assort")
    remition = fields.Float(string="remition")
