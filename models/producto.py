from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    proveedor: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    imagen: Mapped[str] = mapped_column(String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "cantidad": self.cantidad,
            "precio": self.precio,
            "proveedor": self.proveedor,
            "imagen": self.imagen,
        }
