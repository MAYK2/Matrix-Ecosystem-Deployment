from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.domain import CajaPOS, CajaCreate, CajaResponse

router = APIRouter(prefix="/api/caja", tags=["Caja"])

def get_current_user_id():
    # Placeholder for SSO integration. Returning 1 (Admin/Demo)
    return 1

@router.get("/abierta", response_model=CajaResponse)
def get_caja_abierta(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    caja = db.query(CajaPOS).filter(CajaPOS.usuario_id == user_id, CajaPOS.estado == 'abierta').first()
    if not caja:
        raise HTTPException(status_code=404, detail="No hay cajas abiertas para este usuario")
    return caja

@router.post("/abrir", response_model=CajaResponse)
def abrir_caja(caja_in: CajaCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    # Check if already open
    caja_existente = db.query(CajaPOS).filter(CajaPOS.usuario_id == user_id, CajaPOS.estado == 'abierta').first()
    if caja_existente:
        raise HTTPException(status_code=400, detail="Ya existe una caja abierta")
        
    nueva_caja = CajaPOS(
        monto_inicial=caja_in.monto_inicial,
        total_vendido=0,
        diferencia=0,
        estado='abierta',
        usuario_id=user_id,
        medios_pago_json='{"efectivo":0, "tarjeta":0, "transferencia":0, "qr":0}'
    )
    db.add(nueva_caja)
    db.commit()
    db.refresh(nueva_caja)
    
    return nueva_caja

@router.post("/{caja_id}/cerrar")
def cerrar_caja(caja_id: int, monto_final_declarado: float, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    caja = db.query(CajaPOS).filter(CajaPOS.id == caja_id, CajaPOS.usuario_id == user_id, CajaPOS.estado == 'abierta').first()
    if not caja:
        raise HTTPException(status_code=404, detail="Caja no encontrada o ya cerrada")
        
    total_esperado = float(caja.monto_inicial) + float(caja.total_vendido)
    diferencia = monto_final_declarado - total_esperado
    
    caja.estado = 'cerrada'
    caja.fecha_cierre = datetime.utcnow()
    caja.diferencia = diferencia
    
    db.commit()
    return {"message": "Caja cerrada correctamente", "diferencia": diferencia}
