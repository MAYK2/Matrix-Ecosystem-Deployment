from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.domain import Cliente

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

@router.get("/")
def search_clientes(q: str = Query(None, description="Buscar por nombre, dni, cuit o email"), db: Session = Depends(get_db)):
    query = db.query(Cliente)
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Cliente.name.ilike(search_term),
                Cliente.email.ilike(search_term),
                Cliente.phone.ilike(search_term)
            )
        )
    
    clientes = query.limit(50).all()
    results = []
    for c in clientes:
        results.append({
            "id": c.id,
            "nombre": c.name,
            "email": c.email,
            "telefono": c.phone,
            "direccion": c.address,
            "web": c.website,
            "descripcion": c.description,
            "sector": c.sector,
            "instagram": c.instagram,
            "linkedin": c.linkedin,
            "fuente": c.source
        })
    return results

@router.get("/{cliente_id}")
def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    c = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not c:
        return {"error": "Cliente not found"}
        
    return {
        "id": c.id,
        "nombre": c.name,
        "email": c.email,
        "telefono": c.phone,
        "direccion": c.address,
        "web": c.website,
        "descripcion": c.description,
        "sector": c.sector,
        "instagram": c.instagram,
        "facebook": c.facebook,
        "linkedin": c.linkedin,
        "fuente": c.source
    }
