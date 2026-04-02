from typing import List, Optional
from sqlalchemy import select

from models.producto import Producto


class ProductoService:
    def __init__(self, session_factory):
        self.Session = session_factory

    def listar(self) -> List[Producto]:
        with self.Session() as session:
            return session.execute(select(Producto).order_by(Producto.id.desc())).scalars().all()

    def obtener(self, producto_id: int) -> Optional[Producto]:
        with self.Session() as session:
            return session.get(Producto, producto_id)

    def buscar_por_nombre(self, termino: str) -> List[Producto]:
        termino = termino.lower()
        return [p for p in self.listar() if termino in p.nombre.lower()]

    def filtrar_por_categoria(self, categoria: str) -> List[Producto]:
        return [p for p in self.listar() if p.categoria.lower() == categoria.lower()]

    def crear(self, **datos) -> Producto:
        with self.Session() as session:
            producto = Producto(**datos)
            session.add(producto)
            session.commit()
            session.refresh(producto)
            return producto

    def actualizar(self, producto_id: int, **datos) -> bool:
        with self.Session() as session:
            producto = session.get(Producto, producto_id)
            if not producto:
                return False
            for campo, valor in datos.items():
                setattr(producto, campo, valor)
            session.commit()
            return True

    def eliminar(self, producto_id: int) -> bool:
        with self.Session() as session:
            producto = session.get(Producto, producto_id)
            if not producto:
                return False
            session.delete(producto)
            session.commit()
            return True

    def estadisticas(self):
        productos = self.listar()
        return {
            "total_productos": len(productos),
            "total_valor": sum(p.precio * p.cantidad for p in productos),
            "categorias_unicas": len(set(p.categoria for p in productos)),
            "productos_bajo_stock": len([p for p in productos if p.cantidad < 5]),
        }
