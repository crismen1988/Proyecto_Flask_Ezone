"""
Base y utilidades de base de datos compartidas.
Prefiere MySQL cuando la variable de entorno USE_MYSQL no es 0/false.
"""
import os
from sqlalchemy.orm import declarative_base

# Directorio del proyecto (raiz)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Base = declarative_base()


def sqlite_url(db_name: str = "ezone.db") -> str:
    """Construye la URL SQLite local."""
    return f"sqlite:///{os.path.join(PROJECT_ROOT, db_name)}"
