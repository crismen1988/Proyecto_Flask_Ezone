from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Cliente(Base):
    __tablename__ = "clientes"

    ruc: Mapped[str] = mapped_column(String(13), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(120), nullable=False, default="", unique=True)
    direccion: Mapped[str] = mapped_column(String(200), nullable=False, default="")

    def to_dict(self):
        return {
            "ruc": self.ruc,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "email": self.email,
            "direccion": self.direccion,
        }
