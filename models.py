"""
MODELS.PY - EZONE
Modelos ORM y logica del inventario/clientes.
"""

import os

from sqlalchemy import Float, Integer, String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, sessionmaker

BaseInventario = declarative_base()
BaseClientes = declarative_base()


class Producto(BaseInventario):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    proveedor: Mapped[str] = mapped_column(String(100), nullable=False, default="")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "cantidad": self.cantidad,
            "precio": self.precio,
            "proveedor": self.proveedor,
        }


class Cliente(BaseClientes):
    __tablename__ = "clientes"

    ruc: Mapped[str] = mapped_column(String(13), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    direccion: Mapped[str] = mapped_column(String(200), nullable=False, default="")

    def to_dict(self):
        return {
            "ruc": self.ruc,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "email": self.email,
            "direccion": self.direccion,
        }


class Inventario:
    def __init__(self, db_name="inventario.db", clientes_db_name="clientes.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.productos_db = os.path.join(base_dir, db_name)
        self.clientes_db = os.path.join(base_dir, clientes_db_name)

        self.engine_productos = create_engine(f"sqlite:///{self.productos_db}", future=True)
        self.engine_clientes = create_engine(f"sqlite:///{self.clientes_db}", future=True)

        self.SessionProductos = sessionmaker(
            bind=self.engine_productos,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
        self.SessionClientes = sessionmaker(
            bind=self.engine_clientes,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )

        BaseInventario.metadata.create_all(self.engine_productos)
        BaseClientes.metadata.create_all(self.engine_clientes)
        self._normalizar_ruc_clientes()

    def _normalizar_ruc_clientes(self):
        session = self.SessionClientes()
        try:
            clientes = session.execute(select(Cliente)).scalars().all()
            for c in clientes:
                if len(c.ruc) < 13:
                    c.ruc = ("0" * 13 + c.ruc)[-13:]
            session.commit()
        finally:
            session.close()

    def obtener_todos(self):
        session = self.SessionProductos()
        try:
            return session.execute(select(Producto)).scalars().all()
        finally:
            session.close()

    def obtener_por_categoria(self, categoria):
        todos = self.obtener_todos()
        return [p for p in todos if p.categoria.lower() == categoria.lower()]

    def buscar_por_nombre(self, nombre):
        todos = self.obtener_todos()
        return [p for p in todos if nombre.lower() in p.nombre.lower()]

    def agregar_producto(self, nombre, categoria, cantidad, precio, proveedor=""):
        session = self.SessionProductos()
        try:
            nuevo = Producto(
                nombre=nombre,
                categoria=categoria,
                cantidad=cantidad,
                precio=precio,
                proveedor=proveedor or "",
            )
            session.add(nuevo)
            session.commit()
            session.refresh(nuevo)
            return nuevo
        finally:
            session.close()

    def eliminar_producto(self, id_producto):
        session = self.SessionProductos()
        try:
            producto = session.get(Producto, id_producto)
            if not producto:
                return False
            session.delete(producto)
            session.commit()
            return True
        finally:
            session.close()

    def actualizar_producto(self, id_producto, nombre, categoria, cantidad, precio, proveedor=""):
        session = self.SessionProductos()
        try:
            producto = session.get(Producto, id_producto)
            if not producto:
                return False
            producto.nombre = nombre
            producto.categoria = categoria
            producto.cantidad = cantidad
            producto.precio = precio
            producto.proveedor = proveedor or ""
            session.commit()
            return True
        finally:
            session.close()

    def obtener_clientes(self):
        session = self.SessionClientes()
        try:
            return session.execute(select(Cliente).order_by(Cliente.ruc.desc())).scalars().all()
        finally:
            session.close()

    def obtener_cliente_por_id(self, id_cliente):
        session = self.SessionClientes()
        try:
            return session.get(Cliente, id_cliente)
        finally:
            session.close()

    def agregar_cliente(self, ruc, nombre, telefono="", email="", direccion=""):
        session = self.SessionClientes()
        try:
            nuevo = Cliente(
                ruc=ruc,
                nombre=nombre,
                telefono=telefono or "",
                email=email or "",
                direccion=direccion or "",
            )
            session.add(nuevo)
            session.commit()
            return nuevo
        except IntegrityError:
            session.rollback()
            return None
        finally:
            session.close()

    def eliminar_cliente(self, id_cliente):
        session = self.SessionClientes()
        try:
            cliente = session.get(Cliente, id_cliente)
            if not cliente:
                return False
            session.delete(cliente)
            session.commit()
            return True
        finally:
            session.close()

    def actualizar_cliente(self, id_cliente, nuevo_ruc, nombre, telefono="", email="", direccion=""):
        session = self.SessionClientes()
        try:
            cliente = session.get(Cliente, id_cliente)
            if not cliente:
                return False, "no_encontrado"

            if nuevo_ruc != id_cliente:
                existe_nuevo = session.get(Cliente, nuevo_ruc)
                if existe_nuevo:
                    return False, "duplicado"

            cliente.ruc = nuevo_ruc
            cliente.nombre = nombre
            cliente.telefono = telefono or ""
            cliente.email = email or ""
            cliente.direccion = direccion or ""
            session.commit()
            return True, None
        except IntegrityError:
            session.rollback()
            return False, "duplicado"
        finally:
            session.close()

    def obtener_estadisticas(self):
        productos = self.obtener_todos()
        return {
            "total_productos": len(productos),
            "total_valor": sum(p.precio * p.cantidad for p in productos),
            "categorias_unicas": len(set(p.categoria for p in productos)),
            "productos_bajo_stock": len([p for p in productos if p.cantidad < 5]),
        }
