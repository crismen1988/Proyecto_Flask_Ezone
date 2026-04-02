"""
Factory de engine y sesiones SQLAlchemy.
- Prefiere MySQL si USE_MYSQL no es 0/false y la conexión responde.
- Fallback automático a SQLite local.
"""
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from conexion.conexion import get_mysql_engine, mysql_available
from models.base import Base, sqlite_url


def _use_mysql_flag() -> bool:
    flag = os.getenv("USE_MYSQL", "1")
    return flag.strip().lower() not in ("0", "false", "no")


def build_engine():
    if _use_mysql_flag() and mysql_available():
        # Limitar conexiones para evitar max_user_connections
        return get_mysql_engine(echo=False).execution_options(pool_size=1, max_overflow=0)
    # Fallback a SQLite local
    return create_engine(sqlite_url(), future=True, echo=False)


engine = build_engine()
# Evitar exceso de conexiones en MySQL compartido
if engine.dialect.name == "mysql":
    engine.pool.size = 1  # type: ignore
    engine.pool._max_overflow = 0  # type: ignore

# sessionmaker reutilizable para todos los servicios
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def init_db():
    """Crea las tablas si no existen."""
    Base.metadata.create_all(engine)
    _normalizar_ruc()


def _normalizar_ruc():
    """Rellena con ceros a la izquierda los RUC < 13 caracteres."""
    from models.cliente import Cliente  # import local para evitar ciclos

    with SessionLocal() as session:
        clientes = session.execute(select(Cliente)).scalars().all()
        if not clientes:
            return
        changed = False
        for cli in clientes:
            if len(cli.ruc) < 13:
                cli.ruc = ("0" * 13 + cli.ruc)[-13:]
                changed = True
        if changed:
            session.commit()
