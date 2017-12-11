CREATE OR REPLACE FUNCTION issalestock_trg()
  RETURNS trigger AS
$BODY$ DECLARE 
count integer;
BEGIN
select count(id) into  count from stock_picking where name ilike '%OUT%' and id=new.id;
--raise exception '%','ENtro ' || count;
IF count=1 THEN
--raise exception '%','ENtro al if ';
update stock_picking set wni_issale=True where id=new.id;
ELSE
 new.wni_issale:=false;
END IF;

 RETURN NEW;
END 

; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION issalestock_trg()
  OWNER TO postgres;

CREATE TRIGGER issalestock_trg
  after insert 
  ON  stock_picking
  FOR EACH ROW
  EXECUTE PROCEDURE issalestock_trg();



CREATE OR REPLACE FUNCTION accountshipping_trg()
  RETURNS trigger AS
$BODY$ DECLARE 
 v_max integer;
 v_parent integer;
  v_currency integer;
  v_currency_rate  integer;
  v_rate numeric;
  v_name character varying(60);
BEGIN
select parent_id  into v_parent from res_partner where id=new.partner_shipping_id;
	IF v_parent IS NOT NULL THEN
		new.partner_id=v_parent;
  	END IF;
  	select name into v_name from res_currency where id= new.currency_id;
  	IF  v_name ='USD' then
  	
		select id into v_currency from res_currency where name= 'MXN';
		select max(id) into v_currency_rate from res_currency_rate where currency_id= 34;
		select rate into v_rate from res_currency_rate where id= v_currency_rate limit 1;
		--raise exception '%', 'entro al if'|| v_rate;
		new.tipo_cambio:= v_rate;
		
	else
	--raise exception 'entro al if';
		new.tipo_cambio:= 1;
		
	end if;
 RETURN NEW;
END 

; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

ALTER FUNCTION accountshipping_trg()
  OWNER TO odoo;
  CREATE TRIGGER accountshipping_trg
  BEFORE INSERT
  ON account_invoice
  FOR EACH ROW
  EXECUTE PROCEDURE accountshipping_trg();
