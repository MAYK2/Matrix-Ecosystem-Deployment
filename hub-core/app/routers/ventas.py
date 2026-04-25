from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db
from app.models.domain import VentaPOS, VentaPOSDetalle, VentaCreate, CajaPOS, Item

router = APIRouter(prefix="/api/ventas", tags=["Ventas"])

def get_current_user_id():
    return 1 # Placeholder

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_venta(venta_in: VentaCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    # 1. Validar caja
    caja = db.query(CajaPOS).filter(CajaPOS.id == venta_in.caja_id, CajaPOS.estado == 'abierta').with_for_update().first()
    if not caja:
        raise HTTPException(status_code=400, detail="La caja no está abierta o no existe")
        
    # 2. Crear cabecera de la venta
    nueva_venta = VentaPOS(
        caja_id=caja.id,
        cliente_id=venta_in.cliente_id,
        usuario_id=user_id,
        subtotal=venta_in.subtotal,
        descuento_total=venta_in.descuento_total,
        total=venta_in.total,
        medio_pago=venta_in.medio_pago,
        estado='completada'
    )
    db.add(nueva_venta)
    db.flush() # Para obtener el ID de la venta
    
    # 3. Insertar detalles y actualizar stock
    for det in venta_in.detalles:
        item = db.query(Item).filter(Item.id == det.item_id).with_for_update().first()
        if not item:
            raise HTTPException(status_code=400, detail=f"Artículo ID {det.item_id} no encontrado")
            
        detalle_db = VentaPOSDetalle(
            venta_id=nueva_venta.id,
            item_id=item.id,
            cantidad=det.cantidad,
            precio_unitario=det.precio_unitario,
            subtotal=det.cantidad * det.precio_unitario
        )
        db.add(detalle_db)
        
        # Descontar stock
        item.stock -= det.cantidad

    # 4. Actualizar estado de la caja
    caja.total_vendido = float(caja.total_vendido) + venta_in.total
    
    try:
        medios_pago = json.loads(caja.medios_pago_json or '{"efectivo":0, "tarjeta":0, "transferencia":0, "qr":0}')
    except:
        medios_pago = {"efectivo":0, "tarjeta":0, "transferencia":0, "qr":0}
        
    if venta_in.medio_pago in medios_pago:
        medios_pago[venta_in.medio_pago] += venta_in.total
    elif venta_in.medio_pago == 'combinado': # TODO: proper handling of combined payments
        medios_pago['efectivo'] += venta_in.total
        
    caja.medios_pago_json = json.dumps(medios_pago)
    
    db.commit()
    return {"message": "Venta procesada con éxito", "venta_id": nueva_venta.id}
