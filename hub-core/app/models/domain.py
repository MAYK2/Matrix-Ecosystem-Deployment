from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, DECIMAL, Date, Text, Enum
from sqlalchemy.dialects.mysql import INTEGER as MySQLInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Any

from app.database import Base

# ==========================================
# SQLALCHEMY MODELS
# ==========================================

class Item(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), nullable=True, index=True)
    name = Column(String(140), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
    price = Column(DECIMAL(12, 2), default=0.00)
    stock = Column(Integer, default=0, nullable=False)

class Cliente(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150))
    phone = Column(String(50))
    address = Column(String(255))
    website = Column(String(255))
    description = Column(Text)
    sector = Column(String(100))
    instagram = Column(String(150))
    facebook = Column(String(150))
    linkedin = Column(String(150))
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Note: deleting PrecioProducto class since the price is embedded in products

class CajaPOS(Base):
    __tablename__ = "cajas_pos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    monto_inicial = Column(DECIMAL(14, 2), nullable=False, default=0)
    total_vendido = Column(DECIMAL(14, 2), nullable=False, default=0)
    diferencia = Column(DECIMAL(14, 2), nullable=False, default=0)
    medios_pago_json = Column(Text, nullable=True) # JSON with totals per payment method
    estado = Column(Enum('abierta', 'cerrada'), default='abierta', nullable=False)
    fecha_apertura = Column(DateTime, default=datetime.utcnow)
    fecha_cierre = Column(DateTime, nullable=True)
    usuario_id = Column(Integer, nullable=False)

    ventas = relationship("VentaPOS", back_populates="caja")

class VentaPOS(Base):
    __tablename__ = "ventas_pos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    caja_id = Column(Integer, ForeignKey("cajas_pos.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    usuario_id = Column(Integer, nullable=False)
    subtotal = Column(DECIMAL(14, 2), nullable=False, default=0)
    descuento_total = Column(DECIMAL(14, 2), nullable=False, default=0)
    total = Column(DECIMAL(14, 2), nullable=False, default=0)
    medio_pago = Column(Enum('efectivo', 'tarjeta', 'transferencia', 'qr', 'combinado'), nullable=False)
    estado = Column(Enum('completada', 'anulada'), default='completada', nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    caja = relationship("CajaPOS", back_populates="ventas")
    cliente = relationship("Cliente")
    detalles = relationship("VentaPOSDetalle", back_populates="venta", cascade="all, delete-orphan")

class VentaPOSDetalle(Base):
    __tablename__ = "ventas_pos_detalle"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    venta_id = Column(Integer, ForeignKey("ventas_pos.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    cantidad = Column(DECIMAL(12, 2), nullable=False, default=1)
    precio_unitario = Column(DECIMAL(14, 2), nullable=False)
    subtotal = Column(DECIMAL(14, 2), nullable=False)

    venta = relationship("VentaPOS", back_populates="detalles")
    item = relationship("Item")

# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class ItemSchema(BaseModel):
    id: int
    codigo: str
    descripcion: str
    stock: int
    precio_actual: float = 0.0

    model_config = {"from_attributes": True}

class VentaDetalleCreate(BaseModel):
    item_id: int
    cantidad: float
    precio_unitario: float

class VentaCreate(BaseModel):
    caja_id: int
    cliente_id: Optional[int] = None
    subtotal: float
    descuento_total: float
    total: float
    medio_pago: str
    detalles: List[VentaDetalleCreate]

class CajaCreate(BaseModel):
    monto_inicial: float

class CajaResponse(BaseModel):
    id: int
    monto_inicial: float
    total_vendido: float
    estado: str
    
    model_config = {"from_attributes": True}
