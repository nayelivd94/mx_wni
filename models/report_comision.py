
from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists


class ReportStockLinesDate(models.Model):
    _name = "report.comissions"
    _description = "Reporte de Comisiones"
    _auto = False

    id = fields.Integer('Id', readonly=True)
    factura = fields.Many2one('account_invoice', 'Id', readonly=True, index=True)
    date = fields.Char('Mes', readonly=True)
    order = fields.Char('Pedido', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Cliente', readonly=True, index=True)
    executive = fields.Char('Ejecutivo', readonly=True)
    currency = fields.Char('Moneda', readonly=True)
    monto = fields.Float('Monto antes de IVA', readonly=True)
    tipo_cambio= fields.Char('Tipo de Cambio', readonly=True)
    montomxn = fields.Float('Monto en Pesos', readonly=True)
    vendedor = fields.Char('Vendedor', readonly=True)
    nofactura = fields.Char('Factura', readonly=True)
    date_invoice = fields.Date('Fecha de factura', readonly=True)

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'report_comissions')
        self._cr.execute("""
            create or replace view report_comissions as (
                  SELECT i.id,
			        i.id AS factura,
			        (
			            CASE
			                WHEN date_part('month'::text, i.date) = 1::double precision THEN 'Enero'::text
			                WHEN date_part('month'::text, i.date) = 2::double precision THEN 'Febrero'::text
			                WHEN date_part('month'::text, i.date) = 3::double precision THEN 'Marzo'::text
			                WHEN date_part('month'::text, i.date) = 4::double precision THEN 'Abril'::text
			                WHEN date_part('month'::text, i.date) = 5::double precision THEN 'Mayo'::text
			                WHEN date_part('month'::text, i.date) = 6::double precision THEN 'Junio'::text
			                WHEN date_part('month'::text, i.date) = 7::double precision THEN 'Julio'::text
			                WHEN date_part('month'::text, i.date) = 8::double precision THEN 'Agosto'::text
			                WHEN date_part('month'::text, i.date) = 9::double precision THEN 'Septiembre'::text
			                WHEN date_part('month'::text, i.date) = 10::double precision THEN 'Octubre'::text
			                WHEN date_part('month'::text, i.date) = 11::double precision THEN 'Noviembre'::text
			                WHEN date_part('month'::text, i.date) = 12::double precision THEN 'Diciembre'::text
			                ELSE NULL::text
			            END || ' '::text) || date_part('year'::text, i.date) AS date,
			            i.origin AS order,
			            i.partner_id,
			            e.login AS executive,
			            c.name AS currency,
					    (select sum(price_subtotal) from account_invoice_line il
					        Left join product_template  pr on pr.id = il.product_id 
					        where il.invoice_id=i.id  and pr.categ_id not in ('94') ) as monto
					    ,i.tipo_cambio
					    ,(select sum(price_subtotal) from account_invoice_line il
					        Left join product_template  pr on pr.id = il.product_id 
					        where il.invoice_id=i.id  and pr.categ_id not in ('94') ) *i.tipo_cambio as montomxn,
					     rp.name as vendedor,i.state,i.number as nofactura, i.date_invoice
					    from account_invoice i
					      left join res_currency c on c.id=i.currency_id
					      left join res_partner p on i.partner_id = p.id
					      left join res_users u on u.id=i.user_id
					      left join res_users e on e.id=p.user_id
					      left join res_partner rp on rp.id= u.partner_id

					  where 
					   i.state::text = 'paid'::text or i.state::text = 'open'::text  AND date_part('year'::text, i.date) = date_part('year'::text, now())
					   ORDER BY u.login, i.number
            )""")
