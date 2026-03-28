from typing import List
from sqlalchemy import select

from models.factura_detalle import FacturaDetalle


class FacturaDetalleService:
    def __init__(self, session_factory):
        self.Session = session_factory

    def listar_por_factura(self, factura_id: int) -> List[FacturaDetalle]:
        with self.Session() as session:
            return (
                session.execute(
                    select(FacturaDetalle).where(FacturaDetalle.factura_id == factura_id).order_by(FacturaDetalle.id)
                )
                .scalars()
                .all()
            )
