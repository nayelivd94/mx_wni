-- Function: loadseries_trg()

-- DROP FUNCTION loadseries_trg();

CREATE OR REPLACE FUNCTION loadseries_trg()
  RETURNS trigger AS
$BODY$ DECLARE 
v_tmplid integer;
v_producto  integer;
v_lote integer;
v_location integer;
v_RECORD RECORD;
cont integer;
v_productoname character varying(100);
v_stockoperation integer;
v_cont integer;
v_contpr integer;
v_track character varying(20);
--cantidad double;
BEGIN

IF upper(NEW.PRODUCTO) != 'PRODUCTO' OR upper(new.producto) != 'PRODUCTOS' then
	v_productoname:=new.producto;
	SELECT count(id) into v_contpr FROM PRODUCT_PRODUCT where default_code=new.producto;
	IF v_contpr = 0 then
		RAISE EXCEPTION '%','El producto '|| new.producto || ' no esta registrado, favor de revisar el nombre de este.';
	ELSE 
	Select product_tmpl_id into v_tmplid FROM PRODUCT_PRODUCT where default_code=new.producto;
		select tracking into v_track from product_template where id=v_tmplid;
		
		IF v_track ='lot' OR v_track = 'serial' THEN
			--raise exception '%','valor '|| v_track || ' producto '||new.producto;
			select id into v_producto from product_product where default_code=new.producto;
			select count(id) into v_cont from stock_pack_operation where picking_id=new.stockpicking_id and product_id=v_producto;
			IF v_cont = 0 then
				RAISE EXCEPTION '%','En las lineas de tu registro no esta el producto a cargar en excel';
			ELSE 
				select id into v_stockoperation from stock_pack_operation where picking_id=new.stockpicking_id and product_id=v_producto ;
				select spol.lot_id into v_lote from stock_pack_operation_lot spol
				left join stock_production_lot spl on spl.id=spol.lot_id where  spol.operation_id=v_stockoperation and spl.load='t' order by lot_id asc limit 1;
				--RAISE EXCEPTION '%','stockpick' || new.stockpicking_id || 'id de stock '||v_stockoperation;
				update  stock_pack_operation_lot set lot_name=new.serie where lot_id=v_lote;
				UPDATE stock_production_lot SET NAME=NEW.SERIE,load ='f' WHERE id=v_lote ;
				
			END IF;
		END IF;
	END IF;
END IF;

 RETURN NEW;
END 

; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION loadseries_trg()
  OWNER TO postgres;

CREATE TRIGGER  loadseries_trg
  BEFORE INSERT OR UPDATE 
  ON  serie_tmp
  FOR EACH ROW
  EXECUTE PROCEDURE  loadseries_trg();
--DROP TRIGGER loadseries_trg ON SERIE_TMP