from sqlalchemy import Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class FacturaDetalle(Base):
    __tablename__ = "facturas_detalle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    factura_id: Mapped[int] = mapped_column(Integer, ForeignKey("facturas.id", ondelete="CASCADE"), nullable=False)
    producto_id: Mapped[int] = mapped_column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stock_aplicado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto")

    def total(self) -> float:
        return (self.cantidad or 0) * (self.precio_unitario or 0.0)
