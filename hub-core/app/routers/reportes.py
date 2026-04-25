from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.domain import VentaPOS, CajaPOS

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

@router.get("/hoy")
def reportes_hoy(db: Session = Depends(get_db)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    ventas = db.query(VentaPOS).filter(VentaPOS.fecha >= today_start, VentaPOS.estado == 'completada').all()
    
    total_vendido = sum(float(v.total) for v in ventas)
    cantidad = len(ventas)
    ticket_promedio = total_vendido / cantidad if cantidad > 0 else 0
    
    por_medio = {}
    for v in ventas:
        por_medio[v.medio_pago] = por_medio.get(v.medio_pago, 0) + float(v.total)
        
    return {
        "total_vendido": total_vendido,
        "cantidad_operaciones": cantidad,
        "ticket_promedio": ticket_promedio,
        "ventas_por_medio_pago": por_medio
    }

@router.get("/historial")
def historial_ventas(db: Session = Depends(get_db)):
    ventas = db.query(VentaPOS).order_by(VentaPOS.id.desc()).limit(100).all()
    res = []
    for v in ventas:
        res.append({
            "id": v.id,
            "subtotal": v.subtotal,
            "total": v.total,
            "estado": v.estado,
            "fecha": v.fecha.isoformat(),
            "medio_pago": v.medio_pago,
            "cliente_id": v.cliente_id
        })
    return res
