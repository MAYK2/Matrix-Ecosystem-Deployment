import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import engine, Base
# Import all models to create tables
from app.models import domain

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Matrix Flow - Módulo de Ventas", version="1.0")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it runs on local hub, typically you want to allow all or restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routers
from app.routers import productos, clientes, caja, ventas, reportes

app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(caja.router)
app.include_router(ventas.router)
app.include_router(reportes.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import Request
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("pos.html", {"request": request})

@app.get("/clientes", response_class=HTMLResponse)
def clients_page(request: Request):
    return templates.TemplateResponse("clientes.html", {"request": request})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5060))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
