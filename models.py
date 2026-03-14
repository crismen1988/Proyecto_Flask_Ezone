"""
MODELS.PY - EZONE
Modelos ORM y lógica de inventario, clientes y usuarios.
Permite trabajar con SQLite (por defecto) o con MySQL si está configurado.
"""

import os
import sys
from typing import Optional, Tuple

from sqlalchemy import Float, Integer, String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONEXION_DIR = os.path.join(BASE_DIR, "conexion")
if os.path.isdir(CONEXION_DIR) and CONEXION_DIR not in sys.path:
    # Permite importar conexion.py que vive en la carpeta solicitada.
    sys.path.insert(0, CONEXION_DIR)

try:
    from conexion import get_mysql_engine, mysql_available
except Exception:
    # Si el módulo no está disponible (por ejemplo, en un entorno de evaluación sin MySQL),
    # continuamos usando solo SQLite.
    def mysql_available() -> bool:  # type: ignore
        return False

    def get_mysql_engine(*_args, **_kwargs):  # type: ignore
        raise RuntimeError("Soporte MySQL no disponible")


Base = declarative_base()


class Producto(Base):
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


class Cliente(Base):
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


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    mail: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "mail": self.mail,
            "password": self.password,
        }


class Inventario:
    """
    Capa de acceso a datos.
    - Por defecto usa SQLite local (modo sin dependencia externa).
    - Si hay MySQL disponible (mysql_available == True), se usa de forma transparente.
    """

    def __init__(self, db_name: str = "ezone.db", use_mysql: Optional[bool] = None):
        self.sqlite_path = os.path.join(BASE_DIR, db_name)
        self.sqlite_url = f"sqlite:///{self.sqlite_path}"
        # Forzamos MySQL: si falla, levantamos excepción en vez de hacer fallback.
        self.use_mysql = True if use_mysql is None else use_mysql

        self.engine = self._build_engine()
        self.Session = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )

        Base.metadata.create_all(self.engine)
        self._normalizar_ruc_clientes()

    def _build_engine(self):
        if not self.use_mysql:
            raise RuntimeError("MySQL es obligatorio; inicializa Inventario con use_mysql=True.")
        try:
            engine = get_mysql_engine()
            # Hacemos un ping rápido para confirmar que la conexión responde.
            with engine.connect() as conn:
                conn.execute(select(1))
            return engine
        except Exception as exc:
            raise RuntimeError("No se pudo conectar a MySQL. Verifica credenciales/red.") from exc

    # ----------------- PRODUCTOS ----------------- #
    def obtener_todos(self):
        session = self.Session()
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
        session = self.Session()
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
        session = self.Session()
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
        session = self.Session()
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

    # ----------------- CLIENTES ----------------- #
    def obtener_clientes(self):
        session = self.Session()
        try:
            return session.execute(select(Cliente).order_by(Cliente.ruc.desc())).scalars().all()
        finally:
            session.close()

    def obtener_cliente_por_id(self, id_cliente):
        session = self.Session()
        try:
            return session.get(Cliente, id_cliente)
        finally:
            session.close()

    def agregar_cliente(self, ruc, nombre, telefono="", email="", direccion=""):
        session = self.Session()
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
        session = self.Session()
        try:
            cliente = session.get(Cliente, id_cliente)
            if not cliente:
                return False
            session.delete(cliente)
            session.commit()
            return True
        finally:
            session.close()

    def actualizar_cliente(self, id_cliente, nuevo_ruc, nombre, telefono="", email="", direccion="") -> Tuple[bool, Optional[str]]:
        session = self.Session()
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

    def _normalizar_ruc_clientes(self):
        session = self.Session()
        try:
            clientes = session.execute(select(Cliente)).scalars().all()
            for c in clientes:
                if len(c.ruc) < 13:
                    c.ruc = ("0" * 13 + c.ruc)[-13:]
            session.commit()
        finally:
            session.close()

    # ----------------- USUARIOS ----------------- #
    def obtener_usuarios(self):
        session = self.Session()
        try:
            return session.execute(select(Usuario).order_by(Usuario.id_usuario.desc())).scalars().all()
        finally:
            session.close()

    def agregar_usuario(self, nombre: str, mail: str, password: str):
        session = self.Session()
        try:
            nuevo = Usuario(nombre=nombre, mail=mail, password=password)
            session.add(nuevo)
            session.commit()
            session.refresh(nuevo)
            return nuevo
        except IntegrityError:
            session.rollback()
            return None
        finally:
            session.close()

    def eliminar_usuario(self, id_usuario: int) -> bool:
        session = self.Session()
        try:
            usuario = session.get(Usuario, id_usuario)
            if not usuario:
                return False
            session.delete(usuario)
            session.commit()
            return True
        finally:
            session.close()

    def actualizar_usuario(self, id_usuario: int, nombre: str, mail: str, password: str) -> Tuple[bool, Optional[str]]:
        session = self.Session()
        try:
            usuario = session.get(Usuario, id_usuario)
            if not usuario:
                return False, "no_encontrado"

            if usuario.mail != mail:
                existente = session.execute(select(Usuario).where(Usuario.mail == mail)).scalar_one_or_none()
                if existente:
                    return False, "duplicado"

            usuario.nombre = nombre
            usuario.mail = mail
            usuario.password = password
            session.commit()
            return True, None
        except IntegrityError:
            session.rollback()
            return False, "duplicado"
        finally:
            session.close()

    # ----------------- ESTADISTICAS ----------------- #
    def obtener_estadisticas(self):
        productos = self.obtener_todos()
        return {
            "total_productos": len(productos),
            "total_valor": sum(p.precio * p.cantidad for p in productos),
            "categorias_unicas": len(set(p.categoria for p in productos)),
            "productos_bajo_stock": len([p for p in productos if p.cantidad < 5]),
            "motor": "MySQL" if self.use_mysql else "SQLite",
        }
