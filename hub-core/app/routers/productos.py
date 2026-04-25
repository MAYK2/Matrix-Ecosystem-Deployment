from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.domain import Item

router = APIRouter(prefix="/api/productos", tags=["Productos"])

@router.get("/")
def search_productos(q: str = Query(None, description="Buscar por código o descripción"), db: Session = Depends(get_db)):
    query = db.query(Item).filter(Item.active == True)
    if q:
        search_term = f"%{q}%"
        query = query.filter(or_(Item.code.ilike(search_term), Item.name.ilike(search_term)))
    
    # Limit to 50 results for quick POS searching
    items = query.limit(50).all()
    
    results = []
    for item in items:
        results.append({
            "id": item.id,
            "codigo": item.code,
            "descripcion": item.name,
            "stock": item.stock,
            "precio": float(item.price) if item.price else 0.0
        })
    return results

@router.get("/{item_id}")
def get_producto(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return {"error": "Item not found"}
    
    return {
        "id": item.id,
        "codigo": item.code,
        "descripcion": item.name,
        "stock": item.stock,
        "precio": float(item.price) if item.price else 0.0
    }
