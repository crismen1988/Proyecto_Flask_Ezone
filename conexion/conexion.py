"""
Configuración centralizada para conectarse a MySQL desde Flask.

- Lee credenciales desde variables de entorno para evitar hardcodear secretos.
- Expone helpers para obtener la URL de SQLAlchemy y un engine listo.
- Incluye ``mysql_available`` para hacer un ping rápido desde la app.
"""

import os
from typing import Dict

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

# Carga variables desde .env si existe (útil al correr desde IDE)
load_dotenv()

MYSQL_CONFIG: Dict[str, str] = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": os.getenv("MYSQL_PORT", "3306"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "ezone"),
    "ssl": os.getenv("MYSQL_SSL", "0"),  # 1/true para habilitar SSL
}


def get_mysql_url() -> str:
    """
    Construye la URL para SQLAlchemy usando PyMySQL como driver.
    """
    password = MYSQL_CONFIG["password"]
    auth = f"{MYSQL_CONFIG['user']}:{password}" if password else MYSQL_CONFIG["user"]
    return (
        f"mysql+pymysql://{auth}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/"
        f"{MYSQL_CONFIG['database']}?charset=utf8mb4"
    )


def get_mysql_engine(echo: bool = False) -> Engine:
    """
    Retorna un engine SQLAlchemy listo para usarse con MySQL.
    """
    connect_args = {}
    # Algunos proveedores (p. ej. Render + Clever Cloud) exigen SSL
    if MYSQL_CONFIG["ssl"].strip().lower() in ("1", "true", "yes", "on"):
        connect_args["ssl"] = {"ssl": {}}

    return create_engine(
        get_mysql_url(),
        echo=echo,
        future=True,
        pool_pre_ping=True,  # reintenta conexiones que caduquen
        connect_args=connect_args,
    )


def mysql_available() -> bool:
    """
    Hace un ping simple para saber si la conexión está lista.
    No levanta excepción en la app, devuelve False si hay problemas.
    """
    try:
        engine = get_mysql_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except OperationalError:
        return False
    except Exception:
        return False


def raw_mysql_connection():
    """
    Devuelve una conexión cruda usando el driver mysqlclient si se necesita
    ejecutar SQL manual. Se importa solo cuando se llama para no romper si
    el paquete falta.
    """
    import mysql.connector

    kwargs = {
        "host": MYSQL_CONFIG["host"],
        "port": int(MYSQL_CONFIG["port"]),
        "user": MYSQL_CONFIG["user"],
        "password": MYSQL_CONFIG["password"],
        "database": MYSQL_CONFIG["database"],
    }
    if MYSQL_CONFIG["ssl"].strip().lower() in ("1", "true", "yes", "on"):
        kwargs["ssl_disabled"] = False
    return mysql.connector.connect(**kwargs)
