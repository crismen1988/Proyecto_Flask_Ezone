from typing import List
from sqlalchemy import select

from models.factura import Factura


class FacturaService:
    def __init__(self, session_factory):
        self.Session = session_factory

    def listar(self) -> List[Factura]:
        with self.Session() as session:
            return session.execute(select(Factura).order_by(Factura.fecha.desc(), Factura.id.desc())).scalars().all()

    def crear(self, fecha, numero: str, cliente: str, total: float, estado: str = "pendiente") -> Factura:
        with self.Session() as session:
            factura = Factura(
                fecha=fecha,
                numero=numero,
                cliente=cliente,
                total=total,
                estado=estado,
            )
            session.add(factura)
            session.commit()
            session.refresh(factura)
            return factura
