

CREATE OR REPLACE FUNCTION clavepartner_trg()
  RETURNS trigger AS
$BODY$ DECLARE 
 v_max integer;
 v_total integer;
BEGIN
--select * from stock_pack_operation  
 SELECT max(wnii_clave::integer) into v_max from res_partner;
v_total := v_max+1;
NEW.WNII_CLAVE := v_total::text;
 RETURN NEW;
END 

; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION clavepartner_trg()
  OWNER TO postgres;


CREATE TRIGGER  clavepartner_trg
  BEFORE INSERT
  ON res_partner
  FOR EACH ROW
  EXECUTE PROCEDURE clavepartner_trg();