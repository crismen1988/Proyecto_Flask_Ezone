from typing import List
from sqlalchemy import select

from models.solicitud import Solicitud


class SolicitudService:
    def __init__(self, session_factory):
        self.Session = session_factory

    def crear(self, usuario_id: int, titulo: str, detalle: str) -> Solicitud:
        with self.Session() as session:
            sol = Solicitud(usuario_id=usuario_id, titulo=titulo, detalle=detalle, estado="pendiente")
            session.add(sol)
            session.commit()
            session.refresh(sol)
            return sol

    def listar_por_usuario(self, usuario_id: int) -> List[Solicitud]:
        with self.Session() as session:
            return session.execute(
                select(Solicitud).where(Solicitud.usuario_id == usuario_id).order_by(Solicitud.id.desc())
            ).scalars().all()

    def listar_todas(self) -> List[Solicitud]:
        with self.Session() as session:
            return session.execute(select(Solicitud).order_by(Solicitud.id.desc())).scalars().all()

    def actualizar_estado(self, solicitud_id: int, estado: str) -> bool:
        with self.Session() as session:
            sol = session.get(Solicitud, solicitud_id)
            if not sol:
                return False
            sol.estado = estado
            session.commit()
            return True
