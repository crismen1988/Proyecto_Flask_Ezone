"""
MODELS.PY - EZONE
Clases de dominio y logica del inventario.
"""

from database import DatabaseManager


class Producto:
    def __init__(self, id, nombre, categoria, cantidad, precio, proveedor=""):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.cantidad = cantidad
        self.precio = precio
        self.proveedor = proveedor

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "cantidad": self.cantidad,
            "precio": self.precio,
            "proveedor": self.proveedor,
        }


class Cliente:
    def __init__(self, ruc, nombre, telefono="", email="", direccion=""):
        self.ruc = ruc
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion

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
        self.db = DatabaseManager(
            productos_db=db_name,
            clientes_db=clientes_db_name,
        )
        self._cache = {}
        self._clientes_cache = {}
        self._cargar_a_memoria()
        self._cargar_clientes_a_memoria()

    def _cargar_a_memoria(self):
        rows = self.db.obtener_productos()

        self._cache = {
            row["id"]: Producto(
                row["id"],
                row["nombre"],
                row["categoria"],
                row["cantidad"],
                row["precio"],
                row["proveedor"],
            )
            for row in rows
        }

    def _cargar_clientes_a_memoria(self):
        rows = self.db.obtener_clientes()

        self._clientes_cache = {
            row["ruc"]: Cliente(
                row["ruc"],
                row["nombre"],
                row["telefono"],
                row["email"],
                row["direccion"],
            )
            for row in rows
        }

    def obtener_todos(self):
        self._cargar_a_memoria()
        return list(self._cache.values())

    def obtener_por_categoria(self, categoria):
        todos = self.obtener_todos()
        return [p for p in todos if p.categoria.lower() == categoria.lower()]

    def buscar_por_nombre(self, nombre):
        todos = self.obtener_todos()
        return [p for p in todos if nombre.lower() in p.nombre.lower()]

    def agregar_producto(self, nombre, categoria, cantidad, precio, proveedor=""):
        nuevo_id = self.db.insertar_producto(nombre, categoria, cantidad, precio, proveedor)

        nuevo_prod = Producto(nuevo_id, nombre, categoria, cantidad, precio, proveedor)
        self._cache[nuevo_id] = nuevo_prod
        return nuevo_prod

    def eliminar_producto(self, id_producto):
        self._cargar_a_memoria()
        if id_producto in self._cache:
            if self.db.eliminar_producto(id_producto):
                del self._cache[id_producto]
                return True
        return False

    def actualizar_producto(self, id_producto, nombre, categoria, cantidad, precio, proveedor=""):
        self._cargar_a_memoria()
        if id_producto in self._cache:
            if self.db.actualizar_producto(id_producto, nombre, categoria, cantidad, precio, proveedor):
                self._cache[id_producto].nombre = nombre
                self._cache[id_producto].categoria = categoria
                self._cache[id_producto].cantidad = cantidad
                self._cache[id_producto].precio = precio
                self._cache[id_producto].proveedor = proveedor
                return True
        return False

    def obtener_clientes(self):
        self._cargar_clientes_a_memoria()
        return list(self._clientes_cache.values())

    def obtener_cliente_por_id(self, id_cliente):
        self._cargar_clientes_a_memoria()
        return self._clientes_cache.get(id_cliente)

    def agregar_cliente(self, ruc, nombre, telefono="", email="", direccion=""):
        creado = self.db.insertar_cliente(ruc, nombre, telefono, email, direccion)
        if not creado:
            return None

        nuevo_cliente = Cliente(ruc, nombre, telefono, email, direccion)
        self._clientes_cache[ruc] = nuevo_cliente
        return nuevo_cliente

    def eliminar_cliente(self, id_cliente):
        self._cargar_clientes_a_memoria()
        if id_cliente in self._clientes_cache:
            if self.db.eliminar_cliente(id_cliente):
                del self._clientes_cache[id_cliente]
                return True
        return False

    def actualizar_cliente(self, id_cliente, nuevo_ruc, nombre, telefono="", email="", direccion=""):
        self._cargar_clientes_a_memoria()
        if id_cliente in self._clientes_cache:
            if nuevo_ruc != id_cliente and nuevo_ruc in self._clientes_cache:
                return False, "duplicado"
            actualizado, motivo = self.db.actualizar_cliente(
                id_cliente,
                nuevo_ruc,
                nombre,
                telefono,
                email,
                direccion,
            )
            if not actualizado:
                return False, motivo

            cliente = self._clientes_cache[id_cliente]
            cliente.ruc = nuevo_ruc
            cliente.nombre = nombre
            cliente.telefono = telefono
            cliente.email = email
            cliente.direccion = direccion

            if nuevo_ruc != id_cliente:
                del self._clientes_cache[id_cliente]
            self._clientes_cache[nuevo_ruc] = cliente
            return True, None
        return False, "no_encontrado"

    def obtener_estadisticas(self):
        productos = self.obtener_todos()
        return {
            "total_productos": len(productos),
            "total_valor": sum(p.precio * p.cantidad for p in productos),
            "categorias_unicas": len(set(p.categoria for p in productos)),
            "productos_bajo_stock": len([p for p in productos if p.cantidad < 5]),
        }
