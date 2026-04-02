from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from models.usuario import Usuario


class UsuarioService:
    def __init__(self, session_factory):
        self.Session = session_factory

    def listar(self) -> List[Usuario]:
        with self.Session() as session:
            return session.execute(select(Usuario).order_by(Usuario.id_usuario.desc())).scalars().all()

    def contar(self) -> int:
        with self.Session() as session:
            return session.execute(select(func.count(Usuario.id_usuario))).scalar() or 0

    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        with self.Session() as session:
            return session.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()

    def obtener(self, usuario_id: int) -> Optional[Usuario]:
        with self.Session() as session:
            return session.get(Usuario, usuario_id)

    def crear(self, nombre: str, email: str, password: str, role: str = "user") -> Optional[Usuario]:
        with self.Session() as session:
            try:
                nuevo = Usuario(nombre=nombre, email=email, password=password, role=role)
                session.add(nuevo)
                session.commit()
                session.refresh(nuevo)
                return nuevo
            except IntegrityError:
                session.rollback()
                return None

    def actualizar(self, usuario_id: int, nombre: str, email: str, role: str) -> Tuple[bool, Optional[str]]:
        with self.Session() as session:
            usuario = session.get(Usuario, usuario_id)
            if not usuario:
                return False, "no_encontrado"

            if usuario.email != email:
                existente = session.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
                if existente:
                    return False, "duplicado"
            try:
                usuario.nombre = nombre
                usuario.email = email
                usuario.role = role
                session.commit()
                return True, None
            except IntegrityError:
                session.rollback()
                return False, "duplicado"

    def eliminar(self, usuario_id: int) -> bool:
        with self.Session() as session:
            usuario = session.get(Usuario, usuario_id)
            if not usuario:
                return False
            session.delete(usuario)
            session.commit()
            return True

    def cambiar_password(self, usuario_id: int, password_hash: str) -> bool:
        with self.Session() as session:
            usuario = session.get(Usuario, usuario_id)
            if not usuario:
                return False
            usuario.password = password_hash
            session.commit()
            return True
