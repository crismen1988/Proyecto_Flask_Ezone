from datetime import date

from sqlalchemy import Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Factura(Base):
    __tablename__ = "facturas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    cliente: Mapped[str] = mapped_column(String(120), nullable=False)
    cliente_ruc: Mapped[str | None] = mapped_column(
        String(13), ForeignKey("clientes.ruc", ondelete="SET NULL"), nullable=True
    )
    total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="pendiente")

    detalles = relationship("FacturaDetalle", back_populates="factura", cascade="all, delete-orphan")
    cliente_obj = relationship("Cliente", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "numero": self.numero,
            "cliente": self.cliente,
            "total": self.total,
            "estado": self.estado,
        }
