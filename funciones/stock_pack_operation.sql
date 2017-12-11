
CREATE OR REPLACE FUNCTION stockpackoperation_trg()
  RETURNS trigger AS
$BODY$ DECLARE 
 
BEGIN
--select * from stock_pack_operation  
IF NEW.PRODUCT_QTY  < NEW.QTY_DONE THEN
 Raise exception '%','La cantidad recibida debe ser igual a la cantidad por hacer ';
END IF;

 RETURN NEW;
END 

; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION stockpackoperation_trg()
  OWNER TO postgres;


CREATE TRIGGER  stockpackoperation_trg
  BEFORE INSERT OR UPDATE 
  ON stock_pack_operation
  FOR EACH ROW
  EXECUTE PROCEDURE  stockpackoperation_trg();
