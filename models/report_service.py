
from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists


class ReportService(models.Model):
    _name = "report.service"
    _description = "Reporte de Servicios"
    _auto = False

    id = fields.Integer('Id', readonly=True)
    factura = fields.Many2one('account_invoice', 'factura', readonly=True, index=True)
    date = fields.Char('Fecha', readonly=True)
    order = fields.Char('Pedido', readonly=True)
    service = fields.Char('Servicio', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Cliente', readonly=True, index=True)
    executive = fields.Char('Ejecutivo', readonly=True)
    currency = fields.Char('Moneda', readonly=True)
    monto = fields.Float('Monto', readonly=True)
    tipo_cambio= fields.Char('Tipo de Cambio', readonly=True)
    montomxn = fields.Float('Monto en Pesos', readonly=True)
    vendedor = fields.Char('Vendedor', readonly=True)

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'report_service')
        self._cr.execute("""
            create or replace view report_service as (
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
			    i.origin AS order,pr.name as service,
			    i.partner_id,
			    e.login AS executive,
			    c.name AS currency,
			    ( SELECT sum(price_subtotal) AS sum
			           FROM account_invoice_line 
			             LEFT JOIN product_template pr ON pr.id = product_id
			          WHERE invoice_id = i.id AND pr.type='service' ) AS monto,
			    i.tipo_cambio,
			    (( SELECT sum(price_subtotal) AS sum
			           FROM account_invoice_line 
			             LEFT JOIN product_template pr ON pr.id = product_id
			          WHERE invoice_id = i.id AND pr.type='service'))::double precision * i.tipo_cambio AS montomxn,
			    rp.name as vendedor
			   FROM account_invoice i
			     LEFT JOIN res_currency c ON c.id = i.currency_id
			     left join account_invoice_line il on il.invoice_id=i.id
			     LEFT JOIN product_template pr ON pr.id = il.product_id
			     LEFT JOIN res_partner p ON i.partner_id = p.id
			     LEFT JOIN res_users u ON u.id = i.user_id
			     LEFT JOIN res_users e ON e.id = p.user_id
			     left join res_partner rp on rp.id= u.partner_id
			  WHERE i.state::text = 'paid'::text AND date_part('year'::text, i.date) = date_part('year'::text, now()) and pr.type::text = 'service'::text
			  ORDER BY u.login, i.number
            )""")
