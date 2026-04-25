import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_search_productos():
    response = client.get("/api/productos/?q=none_existing")
    assert response.status_code == 200
    assert type(response.json()) == list

def test_caja_y_venta():
    # Abrir caja
    res_abrir = client.post("/api/caja/abrir", json={"monto_inicial": 1500.0})
    if res_abrir.status_code == 400:
        # Cerrar primero si está abierta
        caja = client.get("/api/caja/abierta").json()
        client.post(f"/api/caja/{caja['id']}/cerrar?monto_final_declarado=1500")
        res_abrir = client.post("/api/caja/abrir", json={"monto_inicial": 1500.0})
    
    assert res_abrir.status_code == 200
    caja_id = res_abrir.json()["id"]

    # Intentar venta con items falsos
    res_venta = client.post("/api/ventas/", json={
        "caja_id": caja_id,
        "subtotal": 100,
        "descuento_total": 0,
        "total": 100,
        "medio_pago": "efectivo",
        "detalles": [
            {"item_id": 999999, "cantidad": 1, "precio_unitario": 100} # Mock item
        ]
    })
    
    # Debería dar un bad request 400 por item no encontrado
    assert res_venta.status_code == 400

    # Cerrar caja
    res_cerrar = client.post(f"/api/caja/{caja_id}/cerrar?monto_final_declarado=1500")
    assert res_cerrar.status_code == 200
