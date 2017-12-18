# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import shutil
import logging
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from datetime import datetime
import operator as py_operator

_logger = logging.getLogger(__name__)

class SaleOrderStock(models.Model):
	
  _inherit ='stock.picking'
  sale_id=fields.Many2one('sale.order',string="Venta")


class SaleOrder(models.Model):
	
  _inherit ='sale.order'
  stock_ids = fields.One2many('stock.picking','sale_id')
  deliverys= fields.Text('Envio', compute="_compute_delivery")

  def _compute_delivery(self):
  	stock_obj = self.env['stock.picking']
	for sale in self:
		idsale = stock_obj.search([('sale_id', '=', sale.id),
								 ('state', '!=', 'cancel')])
		#_logger.info(_("ID de stock: \n%s") % (idsale.id))
		#raise UserError(_("ID de stock: \n%s") % (idsale.id))
		#_logger.info(_("ENTOOOOOOO AL IF  "))
		envio=None
		apa=True
		for sale in idsale:
			_logger.info(_("carrier \n%s ")% (sale.carrier_id.name))
			carriers= sale.carrier_id.name
			if unicode(carriers) is not 'False':
				carrier = sale.carrier_id.name
				carrier='Envio: '+unicode(carrier)
			else:
				carrier=""
			if str(sale.carrier_tracking_ref) is not 'False':
				guia = str(sale.carrier_tracking_ref)
				guia=" No. Guia: "+guia
			else:
				guia=""
			_logger.info(_("ESTA VACIO \n%s ")% (str(guia)))
			if apa== True:
				envio= carrier+guia
				apa=False
			else:
				envio=str(envio)+"\n"+str(carrier)+str(guia)+"   "
				#_logger.info(_("ENVIO Y GUIA: \n%s") % (envio))
		sale.deliverys=envio
class wni_invoiceline(models.Model):

    _inherit = 'account.invoice.line'
    date_pediments= fields.Text('Fecha de Pedimentos')
#class wni_purchaseline(models.Model):
#	_inherit='purchase.order.line'
#	@api.depends('order_id.state', 'move_ids.state')
#	def _compute_qty_received(self):
#		for line in self:
#			if line.order_id.state not in ['purchase','partially_received','received']:
#				_logger.info(_("ENTROOOOOOOOOOOOOOOOOOOOOAL IF: \n\n\n\n"))
#				line.qty_received=0.0
#				continue
#			if line.product_id.type not in ['consu','product']:
#				line.qty_received=line.product_qty
#				continue
#			total=line.qty_received
#			for move in line.move_ids:#				_logger.info(_("ENTROOOO AL for   !!!!!!!!!!!!!!!!!!!!!!!!!!! %s\n") % (total))
#				if move.state=='done':
#					_logger.info(_("ENTROOOO AL IF de done %s\n") % (total))
#					if move.product_uom != line.product_uom:
#						total +=move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
#						_logger.info(_("ENTROOOO AL IF %s\n") % (total))
#					else:
#						total+=move.product_uom_qty
#						_logger.info(_("ENTRO AL ELSE: %s\n") % (total))
#			line.qty_received=total

#class StockBackorderConfirmation(models.TransientModel):
#    _inherit = 'stock.backorder.confirmation'

    #@api.one
    #def _process(self, cancel_backorder=False):
	#	for pack in self.pick_id.pack_operation_ids:
	#		if pack.qty_done > 0:
	#			pack.product_qty = pack.qty_done
	#			p_obj=self.env['purchase.order']
	#			p=p_obj.search([('name', '=', self.pick_id.origin)])
#				_logger.info(_("entro a parcialemente : %s\n") % (p))
	#			p.write({'state':'partially_received'})
	#		else:
	#			pack.unlink()
	#	self.pick_id.do_transfer()
	#	if cancel_backorder:
	#		_logger.info(_("ENTRO  \n%s") % (self.pick_id.id))
	#		backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', self.pick_id.id)])
	#		backorder_pick.action_cancel()
	#		self.pick_id.message_post(body=_("Back order <em>%s</em> <b>cancelled</b>.") % (backorder_pick.name))
	#		purchase_obj = self.env['purchase.order']
	#		purchase = purchase_obj.search([('name', '=', self.pick_id.origin)])
	#		_logger.info(_("NOmbre de la compra : %s\n") % (purchase))
	#		purchase.write({'state':'received'})
