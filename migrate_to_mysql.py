"""
Migrar datos locales (SQLite/archivos) hacia MySQL usando las credenciales de entorno.

Ejecuta:
    USE_MYSQL=1 python migrar_a_mysql.py

Lee datos de:
- ezone.db (nuevo esquema)
- inventario.db y clientes.db (esquema anterior)
- archivos CSV de data/ como último recurso
"""

import os
import sys
from collections import OrderedDict

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from models import Base, Cliente, Inventario, Producto, Usuario

# Rutas de posibles fuentes SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_SOURCES = [
    os.path.join(BASE_DIR, "ezone.db"),
    os.path.join(BASE_DIR, "inventario.db"),
    os.path.join(BASE_DIR, "clientes.db"),
]

DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTOS_CSV = os.path.join(DATA_DIR, "productos_registros.csv")
CLIENTES_CSV = os.path.join(DATA_DIR, "clientes_registros.csv")


def leer_sqlite_tabla(db_path, model):
    if not os.path.exists(db_path):
        return []
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    Session = sessionmaker(bind=engine, future=True)
    with Session() as session:
        try:
            return [obj.to_dict() for obj in session.execute(select(model)).scalars().all()]
        except Exception:
            return []


def leer_productos_archivos():
    if not os.path.exists(PRODUCTOS_CSV):
        return []
    import csv

    with open(PRODUCTOS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        productos = []
        for row in reader:
            try:
                productos.append(
                    {
                        "id": int(row.get("id", 0)) if row.get("id") else None,
                        "nombre": row.get("nombre", ""),
                        "categoria": row.get("categoria", ""),
                        "cantidad": int(row.get("cantidad", 0) or 0),
                        "precio": float(row.get("precio", 0) or 0),
                        "proveedor": row.get("proveedor", "") or "",
                    }
                )
            except Exception:
                continue
        return productos


def leer_clientes_archivos():
    if not os.path.exists(CLIENTES_CSV):
        return []
    import csv

    with open(CLIENTES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        clientes = []
        for row in reader:
            clientes.append(
                {
                    "ruc": row.get("ruc", ""),
                    "nombre": row.get("nombre", ""),
                    "telefono": row.get("telefono", "") or "",
                    "email": row.get("email", "") or "",
                    "direccion": row.get("direccion", "") or "",
                }
            )
        return clientes


def merge_unicos(diccionarios, clave):
    """Mantiene el orden de llegada pero elimina duplicados por clave."""
    almacen = OrderedDict()
    for d in diccionarios:
        k = d.get(clave)
        if not k:
            continue
        almacen[k] = d
    return list(almacen.values())


def main():
    inv_mysql = Inventario(use_mysql=True)
    mysql_session = inv_mysql.Session

    # Asegura tablas en MySQL
    Base.metadata.create_all(inv_mysql.engine)

    # --- Productos ---
    productos_list = []
    for path in SQLITE_SOURCES:
        productos_list.extend(leer_sqlite_tabla(path, Producto))
    if not productos_list:
        productos_list = leer_productos_archivos()
    productos_list = merge_unicos(productos_list, "id")

    # --- Clientes ---
    clientes_list = []
    for path in SQLITE_SOURCES:
        clientes_list.extend(leer_sqlite_tabla(path, Cliente))
    if not clientes_list:
        clientes_list = leer_clientes_archivos()
    clientes_list = merge_unicos(clientes_list, "ruc")

    # --- Usuarios (solo desde ezone.db si existiera) ---
    usuarios_list = leer_sqlite_tabla(os.path.join(BASE_DIR, "ezone.db"), Usuario)
    usuarios_list = merge_unicos(usuarios_list, "id_usuario")

    inserted_prod = inserted_cli = inserted_usr = 0

    with mysql_session() as session:
        for p in productos_list:
            obj = Producto(
                id=p.get("id"),
                nombre=p["nombre"],
                categoria=p["categoria"],
                cantidad=p["cantidad"],
                precio=p["precio"],
                proveedor=p.get("proveedor", ""),
            )
            session.merge(obj)
            inserted_prod += 1

        for c in clientes_list:
            obj = Cliente(
                ruc=c["ruc"],
                nombre=c["nombre"],
                telefono=c.get("telefono", ""),
                email=c.get("email", ""),
                direccion=c.get("direccion", ""),
            )
            session.merge(obj)
            inserted_cli += 1

        for u in usuarios_list:
            email = u.get("email") or u.get("mail")
            if not email:
                # Si no hay correo, no podemos crear el usuario
                continue
            obj = Usuario(
                id_usuario=u.get("id_usuario"),
                nombre=u["nombre"],
                email=email,
                password=u["password"],
            )
            session.merge(obj)
            inserted_usr += 1

        session.commit()

    print(f"Productos migrados: {inserted_prod}")
    print(f"Clientes migrados:  {inserted_cli}")
    print(f"Usuarios migrados:  {inserted_usr}")
    print("Listo. Revisa /bd/estado para confirmar.")


if __name__ == "__main__":
    # Evita ejecutar si no hay MySQL activo
    if os.getenv("USE_MYSQL") != "1":
        print("Activa USE_MYSQL=1 y las variables MYSQL_* antes de correr este script.")
        sys.exit(1)
    main()
