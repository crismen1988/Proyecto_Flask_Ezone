from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.cliente import Cliente


class ClienteService:
    def __init__(self, session_factory):
        self.Session = session_factory

    def listar(self) -> List[Cliente]:
        with self.Session() as session:
            return session.execute(select(Cliente).order_by(Cliente.ruc.desc())).scalars().all()

    def obtener(self, ruc: str) -> Optional[Cliente]:
        with self.Session() as session:
            return session.get(Cliente, ruc)

    def crear(self, **datos) -> Optional[Cliente]:
        with self.Session() as session:
            try:
                cliente = Cliente(**datos)
                session.add(cliente)
                session.commit()
                return cliente
            except IntegrityError:
                session.rollback()
                return None

    def actualizar(self, ruc_actual: str, nuevo_ruc: str, **datos) -> Tuple[bool, Optional[str]]:
        with self.Session() as session:
            cliente = session.get(Cliente, ruc_actual)
            if not cliente:
                return False, "no_encontrado"

            if nuevo_ruc != ruc_actual:
                existe = session.get(Cliente, nuevo_ruc)
                if existe:
                    return False, "duplicado"
            try:
                cliente.ruc = nuevo_ruc
                for campo, valor in datos.items():
                    setattr(cliente, campo, valor)
                session.commit()
                return True, None
            except IntegrityError:
                session.rollback()
                return False, "duplicado"

    def eliminar(self, ruc: str) -> bool:
        with self.Session() as session:
            cliente = session.get(Cliente, ruc)
            if not cliente:
                return False
            session.delete(cliente)
            session.commit()
            return True
