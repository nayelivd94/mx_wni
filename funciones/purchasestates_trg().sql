

-- Function: purchasestates_trg()nuevo

-- DROP FUNCTION purchasestates_trg();

CREATE OR REPLACE FUNCTION purchasestates_trg()
  RETURNS trigger AS
$BODY$ DECLARE 
 v_max integer;
 v_par boolean;
 v_in boolean;
 v_total integer;
 v_totals integer;
 vrecord RECORD;
 v_invoice integer;
 v_received integer;
 v_receiveds integer;
 v_receip integer;
 v_name character varying(90);
 v_state character varying(90);
BEGIN


if new.qty_invoiced!=0 then
--raise exception '%','ENTRO A FACTURAr :)';
 update purchase_order set invoiced=TRUE, invoice_status='no' where id=new.order_id;
	select count(id) into v_total from purchase_order_line where order_id=new.order_id;
	--select count(id) into v_invoice from purchase_order_line where order_id=new.order_id and qty_invoiced!=0;
	select count(id) into v_invoice from purchase_order_line where order_id=new.order_id and qty_invoiced=product_qty;
	if v_invoice = v_total  then
	--raise exception '%','ENTRO AL IF FACTURADA :)'||v_invoice || ' cant, '|| v_total;
	   update purchase_order set invoiced=TRUE, invoice_status='no' where id=new.order_id;
	   --raise exception '%','ENTRO AL IF FACTURADA :)';
	   update purchase_order set invoiced=TRUE, invoice_status='no' where id=new.order_id;
	end if;

end if;
--and v_in is False and v_par is False
select state, partially_invoiced, invoiced into v_state, v_par, v_in from purchase_order where id=new.order_id;
--raise exception '%','ENTRO aqui  :)'|| v_state;
if new.qty_received!=0  and v_state!='received'  then
--raise exception '%','ENTRO :)'|| new.qty_received;
	select count(pol.id) into v_total from purchase_order_line pol
	left join product_product p on p.id=pol.product_id
        left join product_template pt on pt.id=p.product_tmpl_id
        where pt.type!='service' and order_id=new.order_id;
	select count(pol.id) into v_received from purchase_order_line pol
	left join product_product p on p.id=pol.product_id
        left join product_template pt on pt.id=p.product_tmpl_id
         where order_id=new.order_id and qty_received=product_qty and pt.type!='service';
	select name into v_name from purchase_order where id=new.order_id ;
	select count(id) into v_totals  from stock_picking where origin= v_name and state!='cancel';
	select count(id) into v_receiveds  from stock_picking where origin= v_name and state='done' ;
        --raise exception '%','ENTRO :)'||  v_receiveds || ' qty_total '|| v_totals;
---select name from product_template where type='service' limit 2
      	v_receip:=new.qty_received;
	if  v_received  = v_total or v_received > v_total then
	   update purchase_order set state='received' where id=new.order_id;
	   update purchase_order set state='received' where id=new.order_id;
	elsif  v_received  < v_total  and v_received!=0 then

	   update purchase_order set state='partially_received' where id=new.order_id;
	 --raise exception '%','ENTRO :)'||new.qty_received;
	elsif  v_receiveds  = v_totals and v_receiveds!=0  then
		   update purchase_order set state='received' where id=new.order_id;
	end if; 
--raise exception '%','ENTRO :)'||  v_received || ' qty_received '|| new.qty_received;
end if;

 RETURN NEW;
END 

; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION purchasestates_trg()
  OWNER TO odoo;



CREATE TRIGGER purchasestates_trg
  AFTER UPDATE
  ON purchase_order_line
  FOR EACH ROW
  EXECUTE PROCEDURE purchasestates_trg();


 


CREATE OR REPLACE FUNCTION modifystates()
  RETURNS character varying AS
$BODY$ DECLARE
v_RECORD RECORD;
 v_max integer;
 v_total integer;
 vrecord RECORD;
 v_invoice integer;
 v_received integer;
 v_receiveds integer;
  v_totals integer;
  v_account integer;
--select * from res_partner
BEGIN
  FOR v_RECORD IN (select * from purchase_order order by id  asc)
LOOP


	select count(pol.id) into v_total from purchase_order_line pol
	left join product_product p on p.id=pol.product_id
        left join product_template pt on pt.id=p.product_tmpl_id
        where pt.type!='service' and order_id=v_RECORD.id;

	select count(pol.id) into v_received from purchase_order_line pol
	left join product_product p on p.id=pol.product_id
        left join product_template pt on pt.id=p.product_tmpl_id
         where order_id=v_RECORD.id and qty_received=product_qty and pt.type!='service';

	select count(id) into v_totals  from stock_picking where origin= v_RECORD.name and state!='cancel';
	select count(id) into v_receiveds  from stock_picking where origin= v_RECORD.name and state='done' ;
        --raise exception '%','ENTRO :)'||  v_receiveds || ' qty_total '|| v_totals;
        SELECT count(id) into v_account from account_invoice where origin=v_RECORD.name;

      	IF v_RECORD.state='invoiced' or v_RECORD.state='partially_invoiced'then
		if  v_received  = v_total or v_received > v_total  then
				update purchase_order set state='received', invoice_status = 'no', invoiced=True where id=v_RECORD.id;
		elsif  v_received  < v_total  and v_received!=0  then
		   update purchase_order set state='partially_received', invoice_status = 'no', invoiced=True where id=v_RECORD.id;
		 --raise exception '%','ENTRO :)'||new.qty_received;
		elsif  v_receiveds  = v_totals and v_receiveds!=0  then
			   update purchase_order set state='received', invoice_status = 'no', invoiced=True where id=v_RECORD.id;
		else
			update purchase_order set state='purchase', invoice_status = 'no', invoiced=True where id=v_RECORD.id;
		end if;
	END IF;
	IF v_RECORD.state!='received' or v_RECORD.state!='received'then
		update  purchase_order set  invoice_status = 'to invoice' where id=v_RECORD.id;
	END IF;
	IF v_RECORD.state!='purhase' then
		update  purchase_order set  invoice_status = 'to invoice' where id=v_RECORD.id;
	END IF;
	if v_account > 0 then
		update purchase_order set invoice_status = 'no', invoiced=True where id=v_RECORD.id;
	else
		update purchase_order set invoice_status = 'to invoice' where id=v_RECORD.id;
	end if;
 END LOOP;

  RETURN 'hola';
END ; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION  modifystates()
  OWNER TO odoo;
 -- select  modifystates()





















 /**************************************************************PRUEBA DE STOCK_QUANT*****************°





CREATE OR REPLACE FUNCTION stockquant()
  RETURNS character varying AS
$BODY$ DECLARE
v_RECORD RECORD;
v_tmpl_id integer;
v_categid integer;
--select * from res_partner
BEGIN
  FOR v_RECORD IN (select id,product_id from stock_quant order by id  asc)
LOOP
	select product_tmpl_id into v_tmpl_id from product_product where id=v_RECORD.product_id;
	select categ_id into v_categid from product_template where id=v_tmpl_id;
	update stock_quant set categ_id= v_categid where id=v_RECORD.id;
 END LOOP;

  RETURN 'hola';
END ; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION  stockquant()
  OWNER TO odoo;
 -- select  stockquant()
 select * from stock_quant where categ_id is null








 

CREATE OR REPLACE FUNCTION stockquant_trg()
  RETURNS trigger AS
$BODY$ DECLARE 
v_tmpl_id integer;
v_categid integer;
BEGIN

select product_tmpl_id into v_tmpl_id from product_product where id=new.product_id;
	select categ_id into v_categid from product_template where id=v_tmpl_id;
	new.categ_id= v_categid;
	--Raise exception '%','entro' || v_categid;

 RETURN NEW;
END 

; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION stockquant_trg()
  OWNER TO odoo;



CREATE TRIGGER stockquant_trg
  BEFORE INSERT
  ON stock_quant
  FOR EACH ROW
  EXECUTE PROCEDURE stockquant_trg();