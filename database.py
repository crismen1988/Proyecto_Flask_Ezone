"""
DATABASE.PY - EZONE
"""

import os
import sqlite3


class DatabaseManager:
    def __init__(self, productos_db="inventario.db", clientes_db="clientes.db"):
        self.productos_db = productos_db
        self.clientes_db = clientes_db
        self._crear_directorio_db(self.productos_db)
        self._crear_directorio_db(self.clientes_db)
        self.inicializar()

    def _crear_directorio_db(self, db_path):
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def get_productos_conn(self):
        conn = sqlite3.connect(self.productos_db)
        conn.row_factory = sqlite3.Row
        return conn

    def get_clientes_conn(self):
        conn = sqlite3.connect(self.clientes_db)
        conn.row_factory = sqlite3.Row
        return conn

    def inicializar(self):
        conn_productos = self.get_productos_conn()
        cursor_productos = conn_productos.cursor()

        cursor_productos.execute(
            """
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 0,
                precio REAL NOT NULL,
                proveedor TEXT DEFAULT ''
            )
            """
        )

        cursor_productos.execute(
            """
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL
            )
            """
        )

        categorias_ezone = [
            ("Seguridad Electronica",),
            ("Domotica",),
            ("Automatizacion",),
            ("Instalaciones Electricas",),
            ("Camaras IP",),
            ("Alarmas",),
            ("Acceso Control",),
        ]
        cursor_productos.executemany(
            "INSERT OR IGNORE INTO categorias (nombre) VALUES (?)",
            categorias_ezone,
        )

        conn_productos.commit()
        conn_productos.close()

        conn_clientes = self.get_clientes_conn()
        cursor_clientes = conn_clientes.cursor()
        cursor_clientes.execute(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                ruc TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                telefono TEXT DEFAULT '',
                email TEXT DEFAULT '',
                direccion TEXT DEFAULT ''
            )
            """
        )
        cursor_clientes.execute(
            """
            UPDATE clientes
            SET ruc = substr('0000000000000' || ruc, -13, 13)
            WHERE length(ruc) < 13
            """
        )
        conn_clientes.commit()
        conn_clientes.close()

        self._migrar_clientes_desde_inventario()

    def _migrar_clientes_desde_inventario(self):
        if not os.path.exists(self.productos_db):
            return

        conn_clientes = self.get_clientes_conn()
        total_clientes = conn_clientes.execute("SELECT COUNT(*) AS total FROM clientes").fetchone()["total"]
        if total_clientes > 0:
            conn_clientes.close()
            return

        conn_productos = self.get_productos_conn()
        try:
            conn_productos.execute("SELECT 1 FROM clientes LIMIT 1").fetchone()
        except sqlite3.OperationalError:
            conn_productos.close()
            conn_clientes.close()
            return

        legacy_clientes = conn_productos.execute(
            "SELECT ruc, nombre, telefono, email, direccion FROM clientes"
        ).fetchall()
        conn_clientes.executemany(
            """
            INSERT OR IGNORE INTO clientes (ruc, nombre, telefono, email, direccion)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    row["ruc"],
                    row["nombre"],
                    row["telefono"],
                    row["email"],
                    row["direccion"],
                )
                for row in legacy_clientes
            ],
        )
        conn_clientes.commit()
        conn_productos.close()
        conn_clientes.close()

    def obtener_productos(self):
        conn = self.get_productos_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def obtener_clientes(self):
        conn = self.get_clientes_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY ruc DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def insertar_producto(self, nombre, categoria, cantidad, precio, proveedor=""):
        conn = self.get_productos_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO productos (nombre, categoria, cantidad, precio, proveedor)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nombre, categoria, cantidad, precio, proveedor),
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()
        return nuevo_id

    def eliminar_producto(self, id_producto):
        conn = self.get_productos_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conn.commit()
        eliminado = cursor.rowcount > 0
        conn.close()
        return eliminado

    def actualizar_producto(self, id_producto, nombre, categoria, cantidad, precio, proveedor=""):
        conn = self.get_productos_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE productos
            SET nombre=?, categoria=?, cantidad=?, precio=?, proveedor=?
            WHERE id=?
            """,
            (nombre, categoria, cantidad, precio, proveedor, id_producto),
        )
        conn.commit()
        actualizado = cursor.rowcount > 0
        conn.close()
        return actualizado

    def insertar_cliente(self, ruc, nombre, telefono="", email="", direccion=""):
        conn = self.get_clientes_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO clientes (ruc, nombre, telefono, email, direccion)
                VALUES (?, ?, ?, ?, ?)
                """,
                (ruc, nombre, telefono, email, direccion),
            )
            conn.commit()
            creado = True
        except sqlite3.IntegrityError:
            creado = False
        finally:
            conn.close()
        return creado

    def eliminar_cliente(self, id_cliente):
        conn = self.get_clientes_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE ruc = ?", (id_cliente,))
        conn.commit()
        eliminado = cursor.rowcount > 0
        conn.close()
        return eliminado

    def actualizar_cliente(self, id_cliente, nuevo_ruc, nombre, telefono="", email="", direccion=""):
        conn = self.get_clientes_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE clientes
                SET ruc=?, nombre=?, telefono=?, email=?, direccion=?
                WHERE ruc=?
                """,
                (nuevo_ruc, nombre, telefono, email, direccion, id_cliente),
            )
            conn.commit()
            if cursor.rowcount == 0:
                return False, "no_encontrado"
            return True, None
        except sqlite3.IntegrityError:
            return False, "duplicado"
        finally:
            conn.close()
