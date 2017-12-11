# -*- coding: utf-8 -*-
import openerp
from openerp import api, fields, models, _, tools,exceptions
from openerp.exceptions import UserError, RedirectWarning, ValidationError,except_orm
import logging
_logger = logging.getLogger(__name__)
class stockpicking(models.Model):
    _inherit = 'stock.picking'
    valor = fields.Char(string="Valor", compute='_compute_value')
    @api.one
    def _compute_value(self):
        if self.origin is not False:
            self.valor = self.origin[0:2]
        else:
            self.valor = ""

    #@api.onchange('pack_operation_product_ids')
    #def _onchange_origin(self):
    #    if self.pack_operation_product_ids and self.valor <> 'PO':
    #        x = 0
    #        for line in self.pack_operation_product_ids:
     #           if x: break
      #          if line.qty_done > line.product_qty:
      #              raise UserError(_("Error: La cantidad recibida debe ser igual a la cantidad por hacer "))
      #          x += 1

    @api.one
    @api.constrains('pack_operation_product_ids')
    def condiciones(self):
        if self.pack_operation_product_ids and self.valor <> 'PO':
            x = 0
            for line in self.pack_operation_product_ids:
                if x: break
                if line.qty_done > line.product_qty:
                    raise UserError(_('Error: La cantidad recibida debe ser igual a la cantidad por hacer '))
                x += 1


class stockpackoperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.onchange('qty_done')
    def _onchange_origin(self):
        if self.picking_id.valor <> 'PO':
            if self.qty_done > self.product_qty and self.product_qty <>0:
                raise UserError(_("Error: La cantidad recibida debe ser igual a la cantidad por hacer "))

    @api.one
    @api.constrains('qty_done')
    def condicionespack(self):
        if self.picking_id.valor <> 'PO':
            if self.qty_done > self.product_qty:
                raise UserError(_("Error: La cantidad recibida debe ser igual a la cantidad por hacer "))