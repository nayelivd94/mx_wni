
CREATE OR REPLACE FUNCTION incrementcliente()
  RETURNS character varying AS
$BODY$ DECLARE 
v_RECORD RECORD;
v_max character varying(45);
v_total integer;
--select * from res_partner
BEGIN 
  FOR v_RECORD IN (SELECT wnii_clave as clave, id as id FROM res_partner order by id desc)
LOOP
  SELECT max(wnii_clave) into v_max from res_partner;
  --update res_partner set wnii_clave=NULL

  IF  v_max =' ' then
  raise notice '%','entro';
	update res_partner set wnii_clave='1000' where id=1;
  ELSE
	v_total := v_max::integer+1;
	  raise notice '%','antes de max ' || v_total;
	update res_partner set wnii_clave=v_total::text where id=v_RECORD.id;
  END IF;
END LOOP;
  
  RETURN 'hola';
END ; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION incrementcliente()
  OWNER TO postgres;
  select incrementcliente()

