from typing import List
from sqlalchemy import select

from models.factura_detalle import FacturaDetalle
from models.producto import Producto


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

    def aplicar_stock_pendiente(self) -> int:
        """Descuenta stock de productos para detalles no aplicados."""
        with self.Session() as session:
            detalles = (
                session.execute(select(FacturaDetalle).where(FacturaDetalle.stock_aplicado == False))  # noqa: E712
                .scalars()
                .all()
            )
            aplicados = 0
            for d in detalles:
                prod = session.get(Producto, d.producto_id)
                if not prod:
                    d.stock_aplicado = True
                    continue
                prod.cantidad = max(0, (prod.cantidad or 0) - (d.cantidad or 0))
                d.stock_aplicado = True
                aplicados += 1
            session.commit()
            return aplicados
