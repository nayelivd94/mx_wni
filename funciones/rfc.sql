
  --------------------------TRIGGER LOS RFC
CREATE OR REPLACE FUNCTION vatpartner_trg()
  RETURNS trigger AS
$BODY$ DECLARE 
 v_vat character varying(180);
BEGIN
--rAISE EXCEPTION '%','entroo ' ;
--new.vat:=new.wnii_vat;
v_vat:= substring(new.vat from 3 ) ;
--rAISE EXCEPTION '%','valor del rfc ' ||v_vat;
  new.wnii_colonia := v_vat;  
 RETURN NEW;
END 

; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION vatpartner_trg()
  OWNER TO odoo;



CREATE TRIGGER vatpartner_trg
  BEFORE INSERT OR UPDATE
  ON res_partner
  FOR EACH ROW
  EXECUTE PROCEDURE vatpartner_trg();

  --------------------------FUNCION K ACTUALIZA LOS RFC
  
CREATE OR REPLACE FUNCTION vatcliente()
  RETURNS character varying AS
$BODY$ DECLARE 
v_RECORD RECORD;
v_max character varying(45);
v_total integer;
--select * from res_partner
BEGIN 
  FOR v_RECORD IN (select substring(vat from 3 ) as rfc, id from res_partner WHERE vat ilike 'MX%' order by  id asc)
LOOP
  update res_partner set wnii_colonia=v_RECORD.rfc where id=v_RECORD.id;
END LOOP;
  
  RETURN 'hola';
END ; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION vatcliente()
  OWNER TO postgres;
  select vatcliente()





  select substring(vat from 0 for (position('MX' in VAT))) from res_partner WHERE ID=1
select substring(vat from 3 )  from res_partner WHERE vat ilike 'MX%' order by  id asc
select id,vat,name,wnii_colonia from res_partner  WHERE vat ilike 'MX%' order by  id asc