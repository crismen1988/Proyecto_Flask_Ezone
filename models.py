"""
MODELS.PY - EZONE
Modelos ORM y lógica de inventario, clientes y usuarios.
Permite trabajar con SQLite (por defecto) o con MySQL si está configurado.
"""

import os
import sys
from typing import Optional, Tuple

from flask_login import UserMixin
from sqlalchemy import Float, Integer, String, create_engine, select, func, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, sessionmaker, relationship

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


class Usuario(Base, UserMixin):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")

    def get_id(self):
        return str(self.id_usuario)

    def is_admin(self):
        return self.role == "admin"

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "email": self.email,
            "password": self.password,
            "role": self.role,
        }


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(120), nullable=False)
    detalle: Mapped[str] = mapped_column(String(300), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="pendiente")

    usuario = relationship("Usuario")


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

        # Aqui construyo el engine segun la configuracion (MySQL obligado)
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
            # Aqui hago un ping rapido para asegurar que la conexion responde
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

    def agregar_producto(self, nombre, categoria, cantidad, precio, proveedor="", imagen=None):
        session = self.Session()
        try:
            nuevo = Producto(
                nombre=nombre,
                categoria=categoria,
                cantidad=cantidad,
                precio=precio,
                proveedor=proveedor or "",
                imagen=imagen,
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

    def actualizar_producto(self, id_producto, nombre, categoria, cantidad, precio, proveedor="", imagen=None):
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
            if imagen is not None:
                producto.imagen = imagen
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

    def contar_usuarios(self):
        session = self.Session()
        try:
            return session.execute(select(func.count(Usuario.id_usuario))).scalar()
        finally:
            session.close()

    def obtener_usuario_por_email(self, email: str):
        session = self.Session()
        try:
            return session.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
        finally:
            session.close()

    def agregar_usuario(self, nombre: str, email: str, password: str, role: str = "user"):
        session = self.Session()
        try:
            # Creo un usuario nuevo con el rol indicado
            nuevo = Usuario(nombre=nombre, email=email, password=password, role=role)
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

    def actualizar_usuario(self, id_usuario: int, nombre: str, email: str, role: str) -> Tuple[bool, Optional[str]]:
        session = self.Session()
        try:
            usuario = session.get(Usuario, id_usuario)
            if not usuario:
                return False, "no_encontrado"

            if usuario.email != email:
                existente = session.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
                if existente:
                    return False, "duplicado"

            usuario.nombre = nombre
            usuario.email = email
            usuario.role = role
            session.commit()
            return True, None
        except IntegrityError:
            session.rollback()
            return False, "duplicado"
        finally:
            session.close()

    def cambiar_password(self, id_usuario: int, password_hash: str) -> bool:
        session = self.Session()
        try:
            usuario = session.get(Usuario, id_usuario)
            if not usuario:
                return False
            usuario.password = password_hash
            session.commit()
            return True
        finally:
            session.close()

    # ----------------- SOLICITUDES ----------------- #
    def crear_solicitud(self, usuario_id: int, titulo: str, detalle: str):
        session = self.Session()
        try:
            sol = Solicitud(usuario_id=usuario_id, titulo=titulo, detalle=detalle, estado="pendiente")
            session.add(sol)
            session.commit()
            session.refresh(sol)
            return sol
        finally:
            session.close()

    def obtener_solicitudes_usuario(self, usuario_id: int):
        session = self.Session()
        try:
            return session.execute(
                select(Solicitud).where(Solicitud.usuario_id == usuario_id).order_by(Solicitud.id.desc())
            ).scalars().all()
        finally:
            session.close()

    def obtener_solicitudes(self):
        session = self.Session()
        try:
            return session.execute(select(Solicitud).order_by(Solicitud.id.desc())).scalars().all()
        finally:
            session.close()

    def actualizar_estado_solicitud(self, solicitud_id: int, nuevo_estado: str) -> bool:
        session = self.Session()
        try:
            sol = session.get(Solicitud, solicitud_id)
            if not sol:
                return False
            sol.estado = nuevo_estado
            session.commit()
            return True
        finally:
            session.close()

    # ----------------- ESTADISTICAS ----------------- #
    def obtener_estadisticas(self):
        # Calculo estadisticas rapidas para el dashboard
        productos = self.obtener_todos()
        return {
            "total_productos": len(productos),
            "total_valor": sum(p.precio * p.cantidad for p in productos),
            "categorias_unicas": len(set(p.categoria for p in productos)),
            "productos_bajo_stock": len([p for p in productos if p.cantidad < 5]),
            "motor": "MySQL" if self.use_mysql else "SQLite",
        }
