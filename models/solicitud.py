from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(120), nullable=False)
    detalle: Mapped[str] = mapped_column(String(300), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="pendiente")

    usuario = relationship("Usuario")
