"""
APP.PY - EZONE
Aplicacion Flask para gestion de inventario y clientes.
"""

import csv
import json
import os

from flask import Flask, render_template, redirect, url_for, flash, request

from forms import (
    ProductoForm,
    BusquedaForm,
    ClienteForm,
    BusquedaClienteForm,
    UsuarioForm,
)
from models import Inventario

app = Flask(__name__)
app.config["SECRET_KEY"] = "ezone_clave_secreta_seguridad_2024"

inventario = Inventario()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTOS_TXT_FILE = os.path.join(DATA_DIR, "productos_registros.txt")
PRODUCTOS_JSON_FILE = os.path.join(DATA_DIR, "productos_registros.json")
PRODUCTOS_CSV_FILE = os.path.join(DATA_DIR, "productos_registros.csv")
CLIENTES_TXT_FILE = os.path.join(DATA_DIR, "clientes_registros.txt")
CLIENTES_JSON_FILE = os.path.join(DATA_DIR, "clientes_registros.json")
CLIENTES_CSV_FILE = os.path.join(DATA_DIR, "clientes_registros.csv")

os.makedirs(DATA_DIR, exist_ok=True)


def _producto_a_dict(producto):
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "categoria": producto.categoria,
        "cantidad": producto.cantidad,
        "precio": producto.precio,
        "proveedor": producto.proveedor or "",
    }


def _cliente_a_dict(cliente):
    return {
        "ruc": cliente.ruc,
        "nombre": cliente.nombre,
        "telefono": cliente.telefono or "",
        "email": cliente.email or "",
        "direccion": cliente.direccion or "",
    }


def guardar_productos_en_txt(registros_producto):
    with open(PRODUCTOS_TXT_FILE, "w", encoding="utf-8") as file:
        for registro_producto in registros_producto:
            file.write(
                f"{registro_producto['id']}|{registro_producto['nombre']}|"
                f"{registro_producto['categoria']}|{registro_producto['cantidad']}|"
                f"{registro_producto['precio']}|{registro_producto['proveedor']}\n"
            )


def leer_productos_txt():
    registros = []
    if not os.path.exists(PRODUCTOS_TXT_FILE):
        return registros

    with open(PRODUCTOS_TXT_FILE, "r", encoding="utf-8") as file:
        for linea in file:
            contenido = linea.strip()
            if not contenido:
                continue
            partes = contenido.split("|", maxsplit=5)
            if len(partes) == 6:
                registros.append(
                    {
                        "id": partes[0],
                        "nombre": partes[1],
                        "categoria": partes[2],
                        "cantidad": partes[3],
                        "precio": partes[4],
                        "proveedor": partes[5],
                    }
                )
    return registros


def guardar_productos_en_json(registros_producto):
    with open(PRODUCTOS_JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(registros_producto, file, ensure_ascii=False, indent=2)


def leer_productos_json():
    if not os.path.exists(PRODUCTOS_JSON_FILE):
        return []
    with open(PRODUCTOS_JSON_FILE, "r", encoding="utf-8") as file:
        try:
            contenido = json.load(file)
            return contenido if isinstance(contenido, list) else []
        except json.JSONDecodeError:
            return []


def guardar_productos_en_csv(registros_producto):
    with open(PRODUCTOS_CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["id", "nombre", "categoria", "cantidad", "precio", "proveedor"],
        )
        writer.writeheader()
        writer.writerows(registros_producto)


def sincronizar_archivos_desde_inventario():
    registros_producto = [_producto_a_dict(p) for p in inventario.obtener_todos()]
    guardar_productos_en_txt(registros_producto)
    guardar_productos_en_json(registros_producto)
    guardar_productos_en_csv(registros_producto)


def leer_productos_csv():
    if not os.path.exists(PRODUCTOS_CSV_FILE):
        return []
    with open(PRODUCTOS_CSV_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def guardar_clientes_en_txt(registros_cliente):
    with open(CLIENTES_TXT_FILE, "w", encoding="utf-8") as file:
        for registro_cliente in registros_cliente:
            file.write(
                f"{registro_cliente['ruc']}|{registro_cliente['nombre']}|"
                f"{registro_cliente['telefono']}|{registro_cliente['email']}|"
                f"{registro_cliente['direccion']}\n"
            )


def leer_clientes_txt():
    registros = []
    if not os.path.exists(CLIENTES_TXT_FILE):
        return registros

    with open(CLIENTES_TXT_FILE, "r", encoding="utf-8") as file:
        for linea in file:
            contenido = linea.strip()
            if not contenido:
                continue
            partes = contenido.split("|", maxsplit=4)
            if len(partes) == 5:
                registros.append(
                    {
                        "ruc": partes[0],
                        "nombre": partes[1],
                        "telefono": partes[2],
                        "email": partes[3],
                        "direccion": partes[4],
                    }
                )
    return registros


def guardar_clientes_en_json(registros_cliente):
    with open(CLIENTES_JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(registros_cliente, file, ensure_ascii=False, indent=2)


def leer_clientes_json():
    if not os.path.exists(CLIENTES_JSON_FILE):
        return []
    with open(CLIENTES_JSON_FILE, "r", encoding="utf-8") as file:
        try:
            contenido = json.load(file)
            return contenido if isinstance(contenido, list) else []
        except json.JSONDecodeError:
            return []


def guardar_clientes_en_csv(registros_cliente):
    with open(CLIENTES_CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["ruc", "nombre", "telefono", "email", "direccion"],
        )
        writer.writeheader()
        writer.writerows(registros_cliente)


def leer_clientes_csv():
    if not os.path.exists(CLIENTES_CSV_FILE):
        return []
    with open(CLIENTES_CSV_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def sincronizar_archivos_desde_clientes():
    registros_cliente = [_cliente_a_dict(c) for c in inventario.obtener_clientes()]
    guardar_clientes_en_txt(registros_cliente)
    guardar_clientes_en_json(registros_cliente)
    guardar_clientes_en_csv(registros_cliente)


def leer_archivo_como_texto(path_archivo):
    if not os.path.exists(path_archivo):
        return ""
    with open(path_archivo, "r", encoding="utf-8") as file:
        return file.read()


@app.route("/")
def index():
    """
    Pagina principal con accesos a secciones.
    """
    stats = inventario.obtener_estadisticas()
    total_clientes = len(inventario.obtener_clientes())
    return render_template(
        "index.html",
        estadisticas=stats,
        total_clientes=total_clientes,
    )


@app.route("/inventario")
def inventario_view():
    productos = inventario.obtener_todos()
    estadisticas = inventario.obtener_estadisticas()
    return render_template(
        "inventario.html",
        productos=productos,
        estadisticas=estadisticas,
        busqueda_form=BusquedaForm(),
    )


@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    form = ProductoForm()

    if form.validate_on_submit():
        inventario.agregar_producto(
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            cantidad=form.cantidad.data,
            precio=form.precio.data,
            proveedor=form.proveedor.data,
        )
        sincronizar_archivos_desde_inventario()
        flash("Producto agregado y archivos TXT/JSON/CSV sincronizados.", "success")
        return redirect(url_for("inventario_view"))

    return render_template("agregar_producto.html", form=form)


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    form = ProductoForm()

    if request.method == "GET":
        todos = inventario.obtener_todos()
        producto = next((p for p in todos if p.id == id), None)

        if producto:
            form.nombre.data = producto.nombre
            form.categoria.data = producto.categoria
            form.cantidad.data = producto.cantidad
            form.precio.data = producto.precio
            form.proveedor.data = producto.proveedor
        else:
            flash("Producto no encontrado.", "danger")
            return redirect(url_for("inventario_view"))

    if form.validate_on_submit():
        actualizado = inventario.actualizar_producto(
            id_producto=id,
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            cantidad=form.cantidad.data,
            precio=form.precio.data,
            proveedor=form.proveedor.data,
        )
        if actualizado:
            sincronizar_archivos_desde_inventario()
            flash("Producto actualizado y archivos sincronizados.", "info")
        else:
            flash("No se pudo actualizar el producto.", "danger")
        return redirect(url_for("inventario_view"))

    return render_template("editar_producto.html", form=form, id=id)


@app.route("/eliminar/<int:id>")
def eliminar(id):
    if inventario.eliminar_producto(id):
        sincronizar_archivos_desde_inventario()
        flash("Producto eliminado y archivos sincronizados.", "warning")
    else:
        flash("No se pudo eliminar el producto.", "danger")
    return redirect(url_for("inventario_view"))


@app.route("/buscar", methods=["GET", "POST"])
def buscar():
    form = BusquedaForm()
    productos = []

    if form.validate_on_submit():
        termino = form.termino.data
        categoria = form.categoria_filtro.data

        if termino:
            productos = inventario.buscar_por_nombre(termino)
        elif categoria != "todas":
            productos = inventario.obtener_por_categoria(categoria)
        else:
            productos = inventario.obtener_todos()

    return render_template("buscar_producto.html", form=form, productos=productos)


@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    form = ClienteForm()

    if form.validate_on_submit():
        nuevo_cliente = inventario.agregar_cliente(
            ruc=form.ruc.data,
            nombre=form.nombre.data,
            telefono=form.telefono.data or "",
            email=form.email.data or "",
            direccion=form.direccion.data or "",
        )
        if nuevo_cliente is None:
            flash("El RUC ya existe. Usa uno diferente.", "danger")
            lista_clientes = inventario.obtener_clientes()
            return render_template("clientes.html", form=form, clientes=lista_clientes)
        sincronizar_archivos_desde_clientes()
        flash("Cliente agregado correctamente.", "success")
        return redirect(url_for("clientes"))

    lista_clientes = inventario.obtener_clientes()

    return render_template(
        "clientes.html",
        form=form,
        clientes=lista_clientes,
    )


@app.route("/clientes/buscar", methods=["GET", "POST"])
def buscar_cliente():
    form = BusquedaClienteForm()
    clientes_encontrados = []

    if form.validate_on_submit():
        termino = form.termino.data.strip().lower()
        clientes_encontrados = [
            cliente
            for cliente in inventario.obtener_clientes()
            if termino in cliente.nombre.lower() or termino in cliente.ruc.lower()
        ]

    return render_template(
        "buscar_cliente.html",
        form=form,
        clientes=clientes_encontrados,
    )


@app.route("/clientes/eliminar/<string:ruc>", methods=["POST"])
def eliminar_cliente(ruc):
    if inventario.eliminar_cliente(ruc):
        sincronizar_archivos_desde_clientes()
        flash("Cliente eliminado.", "warning")
    else:
        flash("No se pudo eliminar el cliente.", "danger")
    return redirect(url_for("clientes"))


@app.route("/clientes/editar/<string:ruc>", methods=["GET", "POST"])
def editar_cliente(ruc):
    cliente = inventario.obtener_cliente_por_id(ruc)
    if not cliente:
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for("clientes"))

    form = ClienteForm()

    if request.method == "GET":
        form.ruc.data = cliente.ruc
        form.nombre.data = cliente.nombre
        form.telefono.data = cliente.telefono
        form.email.data = cliente.email
        form.direccion.data = cliente.direccion

    if form.validate_on_submit():
        actualizado, motivo = inventario.actualizar_cliente(
            id_cliente=ruc,
            nuevo_ruc=form.ruc.data,
            nombre=form.nombre.data,
            telefono=form.telefono.data or "",
            email=form.email.data or "",
            direccion=form.direccion.data or "",
        )
        if not actualizado:
            if motivo == "duplicado":
                flash("El RUC ingresado ya existe.", "danger")
            else:
                flash("No se pudo actualizar el cliente.", "danger")
            cliente = inventario.obtener_cliente_por_id(ruc) or cliente
            return render_template("editar_cliente.html", form=form, cliente=cliente)

        sincronizar_archivos_desde_clientes()
        flash("Cliente actualizado correctamente.", "info")
        return redirect(url_for("clientes"))

    return render_template("editar_cliente.html", form=form, cliente=cliente)


@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    """
    CRUD básico para la tabla usuarios (MySQL/SQLite).
    """
    form = UsuarioForm()
    if form.validate_on_submit():
        nuevo = inventario.agregar_usuario(
            nombre=form.nombre.data,
            mail=form.mail.data,
            password=form.password.data,
        )
        if nuevo is None:
            flash("El correo ya existe. Usa uno diferente.", "danger")
        else:
            flash("Usuario guardado correctamente.", "success")
        return redirect(url_for("usuarios"))

    lista_usuarios = inventario.obtener_usuarios()
    return render_template(
        "usuarios.html",
        form=form,
        usuarios=lista_usuarios,
        motor=inventario.use_mysql,
    )


@app.route("/usuarios/eliminar/<int:id_usuario>", methods=["POST"])
def eliminar_usuario(id_usuario):
    if inventario.eliminar_usuario(id_usuario):
        flash("Usuario eliminado.", "warning")
    else:
        flash("No se pudo eliminar el usuario.", "danger")
    return redirect(url_for("usuarios"))


@app.route("/usuarios/editar/<int:id_usuario>", methods=["GET", "POST"])
def editar_usuario(id_usuario):
    usuarios = inventario.obtener_usuarios()
    usuario = next((u for u in usuarios if u.id_usuario == id_usuario), None)
    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("usuarios"))

    form = UsuarioForm()

    if request.method == "GET":
        form.nombre.data = usuario.nombre
        form.mail.data = usuario.mail
        form.password.data = usuario.password

    if form.validate_on_submit():
        actualizado, motivo = inventario.actualizar_usuario(
            id_usuario=id_usuario,
            nombre=form.nombre.data,
            mail=form.mail.data,
            password=form.password.data,
        )
        if not actualizado:
            if motivo == "duplicado":
                flash("El correo ya existe.", "danger")
            else:
                flash("No se pudo actualizar el usuario.", "danger")
            return render_template("editar_usuario.html", form=form, usuario=usuario)

        flash("Usuario actualizado correctamente.", "info")
        return redirect(url_for("usuarios"))

    return render_template("editar_usuario.html", form=form, usuario=usuario)


@app.route("/bd/estado")
def estado_bd():
    """
    Muestra información de la conexión activa (MySQL o SQLite).
    """
    stats = inventario.obtener_estadisticas()
    return render_template(
        "estado_bd.html",
        motor=stats.get("motor"),
        total_productos=stats.get("total_productos"),
        total_clientes=len(inventario.obtener_clientes()),
        total_usuarios=len(inventario.obtener_usuarios()),
    )


@app.route("/persistencia/archivos", methods=["GET"])
def persistencia_archivos():
    sincronizar_archivos_desde_inventario()
    sincronizar_archivos_desde_clientes()
    return render_template(
        "persistencia_archivos.html",
        registros_productos_txt=leer_productos_txt(),
        registros_productos_json=leer_productos_json(),
        registros_productos_csv=leer_productos_csv(),
        registros_clientes_txt=leer_clientes_txt(),
        registros_clientes_json=leer_clientes_json(),
        registros_clientes_csv=leer_clientes_csv(),
        contenido_productos_txt=leer_archivo_como_texto(PRODUCTOS_TXT_FILE),
        contenido_productos_json=leer_archivo_como_texto(PRODUCTOS_JSON_FILE),
        contenido_productos_csv=leer_archivo_como_texto(PRODUCTOS_CSV_FILE),
        contenido_clientes_txt=leer_archivo_como_texto(CLIENTES_TXT_FILE),
        contenido_clientes_json=leer_archivo_como_texto(CLIENTES_JSON_FILE),
        contenido_clientes_csv=leer_archivo_como_texto(CLIENTES_CSV_FILE),
    )


@app.errorhandler(404)
def error_404(_e):
    return render_template("index.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)

