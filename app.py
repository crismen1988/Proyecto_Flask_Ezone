"""
APP.PY - EZONE
Aplicacion Flask organizada en capas (models, services, forms) con CRUD y reporte PDF.
"""
import csv
import json
import os
import io
from uuid import uuid4
from datetime import timedelta

from flask import Flask, render_template, redirect, url_for, flash, request, Response, send_file, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from forms import (
    ProductoForm,
    BusquedaForm,
    ClienteForm,
    BusquedaClienteForm,
    UsuarioForm,
    LoginForm,
    ProfileForm,
    PasswordChangeForm,
    SolicitudForm,
)
from services import (
    SessionLocal,
    init_db,
    ProductoService,
    ClienteService,
    UsuarioService,
    SolicitudService,
    FacturaService,
    FacturaDetalleService,
)
from models import Factura, FacturaDetalle
from services.db import engine
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Reporte PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


app = Flask(__name__)
app.config["SECRET_KEY"] = "ezone_clave_secreta_seguridad_2024"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Inicializar DB y servicios
init_db()
producto_service = ProductoService(SessionLocal)
cliente_service = ClienteService(SessionLocal)
usuario_service = UsuarioService(SessionLocal)
solicitud_service = SolicitudService(SessionLocal)
factura_service = FacturaService(SessionLocal)
factura_detalle_service = FacturaDetalleService(SessionLocal)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    try:
        return usuario_service.obtener(int(user_id))
    except Exception:
        return None


# ----------------- Archivos auxiliares ----------------- #
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
        "imagen": producto.imagen or "",
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
                f"{registro_producto['precio']}|{registro_producto['proveedor']}|{registro_producto.get('imagen','')}\n"
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
            partes = contenido.split("|", maxsplit=6)
            if len(partes) >= 6:
                registros.append(
                    {
                        "id": partes[0],
                        "nombre": partes[1],
                        "categoria": partes[2],
                        "cantidad": partes[3],
                        "precio": partes[4],
                        "proveedor": partes[5],
                        "imagen": partes[6] if len(partes) > 6 else "",
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
            fieldnames=["id", "nombre", "categoria", "cantidad", "precio", "proveedor", "imagen"],
        )
        writer.writeheader()
        writer.writerows(registros_producto)


def sincronizar_archivos_desde_productos():
    registros_producto = [_producto_a_dict(p) for p in producto_service.listar()]
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
    registros_cliente = [_cliente_a_dict(c) for c in cliente_service.listar()]
    guardar_clientes_en_txt(registros_cliente)
    guardar_clientes_en_json(registros_cliente)
    guardar_clientes_en_csv(registros_cliente)


def leer_archivo_como_texto(path_archivo):
    if not os.path.exists(path_archivo):
        return ""
    with open(path_archivo, "r", encoding="utf-8") as file:
        return file.read()


# ----------------- Autenticación ----------------- #
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = UsuarioForm()
    if form.validate_on_submit():
        user_count = usuario_service.contar()
        role = "admin" if user_count == 0 else "user"
        hashed_password = generate_password_hash(form.password.data)
        nuevo = usuario_service.crear(
            nombre=form.nombre.data,
            email=form.email.data,
            password=hashed_password,
            role=role,
        )
        if nuevo is None:
            flash("El correo ya existe. Usa uno diferente.", "danger")
        else:
            flash(f"Usuario registrado correctamente como {role}. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = usuario_service.obtener_por_email(form.email.data)
        if user is None:
            flash("Correo o contraseña incorrectos.", "danger")
        elif check_password_hash(user.password, form.password.data):
            login_user(user)
            session.permanent = True  # activa expiración por inactividad
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("index"))


# ----------------- Productos CRUD ----------------- #
@app.route("/")
@login_required
def index():
    stats = producto_service.estadisticas()
    total_clientes = len(cliente_service.listar())
    return render_template(
        "index.html",
        estadisticas=stats,
        total_clientes=total_clientes,
    )


@app.route("/inventario")
@login_required
def inventario_view():
    productos = producto_service.listar()
    estadisticas = producto_service.estadisticas()
    return render_template(
        "productos/inventario.html",
        productos=productos,
        estadisticas=estadisticas,
        busqueda_form=BusquedaForm(),
    )


@app.route("/agregar", methods=["GET", "POST"])
@login_required
def agregar():
    form = ProductoForm()
    if form.validate_on_submit():
        imagen_valor = None
        if form.imagen_archivo.data and form.imagen_archivo.data.filename:
            filename = secure_filename(form.imagen_archivo.data.filename)
            if filename:
                nombre_unico = f"{uuid4().hex}_{filename}"
                ruta_destino = os.path.join(app.config["UPLOAD_FOLDER"], nombre_unico)
                form.imagen_archivo.data.save(ruta_destino)
                imagen_valor = f"uploads/{nombre_unico}"
        elif form.imagen_url.data:
            imagen_valor = form.imagen_url.data.strip()

        producto_service.crear(
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            cantidad=form.cantidad.data,
            precio=form.precio.data,
            proveedor=form.proveedor.data,
            imagen=imagen_valor,
        )
        sincronizar_archivos_desde_productos()
        flash("Producto agregado y archivos TXT/JSON/CSV sincronizados.", "success")
        return redirect(url_for("inventario_view"))
    return render_template("productos/agregar_producto.html", form=form)


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    form = ProductoForm()
    producto = producto_service.obtener(id)

    if request.method == "GET":
        if producto:
            form.nombre.data = producto.nombre
            form.categoria.data = producto.categoria
            form.cantidad.data = producto.cantidad
            form.precio.data = producto.precio
            form.proveedor.data = producto.proveedor
            if producto.imagen and producto.imagen.startswith("http"):
                form.imagen_url.data = producto.imagen
        else:
            flash("Producto no encontrado.", "danger")
            return redirect(url_for("inventario_view"))

    if form.validate_on_submit():
        imagen_valor = None
        if form.imagen_archivo.data and form.imagen_archivo.data.filename:
            filename = secure_filename(form.imagen_archivo.data.filename)
            if filename:
                nombre_unico = f"{uuid4().hex}_{filename}"
                ruta_destino = os.path.join(app.config["UPLOAD_FOLDER"], nombre_unico)
                form.imagen_archivo.data.save(ruta_destino)
                imagen_valor = f"uploads/{nombre_unico}"
        elif form.imagen_url.data:
            imagen_valor = form.imagen_url.data.strip()
        elif producto:
            imagen_valor = producto.imagen

        actualizado = producto_service.actualizar(
            producto_id=id,
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            cantidad=form.cantidad.data,
            precio=form.precio.data,
            proveedor=form.proveedor.data,
            imagen=imagen_valor,
        )
        if actualizado:
            sincronizar_archivos_desde_productos()
            flash("Producto actualizado y archivos sincronizados.", "info")
        else:
            flash("No se pudo actualizar el producto.", "danger")
        return redirect(url_for("inventario_view"))

    return render_template("productos/editar_producto.html", form=form, id=id, producto=producto)


@app.route("/eliminar/<int:id>")
@login_required
def eliminar(id):
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden eliminar productos.", "danger")
        return redirect(url_for("inventario_view"))
    if producto_service.eliminar(id):
        sincronizar_archivos_desde_productos()
        flash("Producto eliminado y archivos sincronizados.", "warning")
    else:
        flash("No se pudo eliminar el producto.", "danger")
    return redirect(url_for("inventario_view"))


@app.route("/buscar", methods=["GET", "POST"])
@login_required
def buscar():
    form = BusquedaForm()
    productos = []
    if form.validate_on_submit():
        termino = form.termino.data
        categoria = form.categoria_filtro.data
        if termino:
            productos = producto_service.buscar_por_nombre(termino)
        elif categoria != "todas":
            productos = producto_service.filtrar_por_categoria(categoria)
        else:
            productos = producto_service.listar()
    return render_template("productos/buscar_producto.html", form=form, productos=productos)


# ----------------- Clientes ----------------- #
@app.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    form = ClienteForm()
    if form.validate_on_submit():
        nuevo_cliente = cliente_service.crear(
            ruc=form.ruc.data,
            nombre=form.nombre.data,
            telefono=form.telefono.data or "",
            email=form.email.data or "",
            direccion=form.direccion.data or "",
        )
        if nuevo_cliente is None:
            flash("El RUC ya existe. Usa uno diferente.", "danger")
            lista_clientes = cliente_service.listar()
            return render_template("clientes.html", form=form, clientes=lista_clientes)
        sincronizar_archivos_desde_clientes()
        flash("Cliente agregado correctamente.", "success")
        return redirect(url_for("clientes"))

    lista_clientes = cliente_service.listar()
    return render_template("clientes.html", form=form, clientes=lista_clientes)


@app.route("/clientes/buscar", methods=["GET", "POST"])
@login_required
def buscar_cliente():
    form = BusquedaClienteForm()
    clientes_encontrados = []
    if form.validate_on_submit():
        termino = form.termino.data.strip().lower()
        clientes_encontrados = [
            cliente
            for cliente in cliente_service.listar()
            if termino in cliente.nombre.lower() or termino in cliente.ruc.lower()
        ]
    return render_template("buscar_cliente.html", form=form, clientes=clientes_encontrados)


@app.route("/clientes/eliminar/<string:ruc>", methods=["POST"])
@login_required
def eliminar_cliente(ruc):
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden eliminar clientes.", "danger")
        return redirect(url_for("clientes"))
    if cliente_service.eliminar(ruc):
        sincronizar_archivos_desde_clientes()
        flash("Cliente eliminado.", "warning")
    else:
        flash("No se pudo eliminar el cliente.", "danger")
    return redirect(url_for("clientes"))


@app.route("/clientes/editar/<string:ruc>", methods=["GET", "POST"])
@login_required
def editar_cliente(ruc):
    cliente = cliente_service.obtener(ruc)
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
        actualizado, motivo = cliente_service.actualizar(
            ruc_actual=ruc,
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
            cliente = cliente_service.obtener(ruc) or cliente
            return render_template("editar_cliente.html", form=form, cliente=cliente)

        sincronizar_archivos_desde_clientes()
        flash("Cliente actualizado correctamente.", "info")
        return redirect(url_for("clientes"))

    return render_template("editar_cliente.html", form=form, cliente=cliente)


# ----------------- Usuarios ----------------- #
@app.route("/usuarios", methods=["GET", "POST"])
@login_required
def usuarios():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden gestionar usuarios.", "danger")
        return redirect(url_for("index"))
    form = UsuarioForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        nuevo = usuario_service.crear(
            nombre=form.nombre.data,
            email=form.email.data,
            password=hashed_password,
        )
        if nuevo is None:
            flash("El correo ya existe. Usa uno diferente.", "danger")
        else:
            flash("Usuario guardado correctamente.", "success")
        return redirect(url_for("usuarios"))

    lista_usuarios = usuario_service.listar()
    motor = "MySQL" if engine.dialect.name == "mysql" else "SQLite"
    return render_template(
        "usuarios.html",
        form=form,
        usuarios=lista_usuarios,
        motor=motor,
    )


@app.route("/usuarios/eliminar/<int:id_usuario>", methods=["POST"])
@login_required
def eliminar_usuario(id_usuario):
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden gestionar usuarios.", "danger")
        return redirect(url_for("index"))
    if usuario_service.eliminar(id_usuario):
        flash("Usuario eliminado.", "warning")
    else:
        flash("No se pudo eliminar el usuario.", "danger")
    return redirect(url_for("usuarios"))


@app.route("/usuarios/editar/<int:id_usuario>", methods=["GET", "POST"])
@login_required
def editar_usuario(id_usuario):
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden gestionar usuarios.", "danger")
        return redirect(url_for("index"))
    usuario = usuario_service.obtener(id_usuario)
    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("usuarios"))

    form = UsuarioForm()
    if request.method == "GET":
        form.nombre.data = usuario.nombre
        form.email.data = usuario.email

    if form.validate_on_submit():
        actualizado, motivo = usuario_service.actualizar(
            usuario_id=id_usuario,
            nombre=form.nombre.data,
            email=form.email.data,
            role=usuario.role,
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


# ----------------- Estado BD y persistencia ----------------- #
@app.route("/bd/estado")
def estado_bd():
    stats = producto_service.estadisticas()
    return render_template(
        "estado_bd.html",
        motor="MySQL" if engine.dialect.name == "mysql" else "SQLite",
        total_productos=stats.get("total_productos"),
        total_clientes=len(cliente_service.listar()),
        total_usuarios=len(usuario_service.listar()),
    )


@app.route("/persistencia/archivos", methods=["GET"])
def persistencia_archivos():
    sincronizar_archivos_desde_productos()
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


# ----------------- Cuenta de usuario ----------------- #
@app.route("/mi_cuenta", methods=["GET", "POST"])
@login_required
def mi_cuenta():
    perfil_form = ProfileForm()
    pwd_form = PasswordChangeForm()

    if request.method == "GET":
        perfil_form.nombre.data = current_user.nombre
        perfil_form.email.data = current_user.email

    if perfil_form.enviar.data and perfil_form.validate_on_submit():
        actualizado, motivo = usuario_service.actualizar(
            usuario_id=current_user.id_usuario,
            nombre=perfil_form.nombre.data,
            email=perfil_form.email.data,
            role=current_user.role,
        )
        if not actualizado:
            mensaje = "El correo ya existe." if motivo == "duplicado" else "No se pudo actualizar tu perfil."
            flash(mensaje, "danger")
        else:
            flash("Perfil actualizado.", "success")
        return redirect(url_for("mi_cuenta"))

    if pwd_form.enviar.data and pwd_form.validate_on_submit():
        if not check_password_hash(current_user.password, pwd_form.password_actual.data):
            flash("La contraseña actual es incorrecta.", "danger")
            return redirect(url_for("mi_cuenta"))
        nuevo_hash = generate_password_hash(pwd_form.password_nueva.data)
        if usuario_service.cambiar_password(current_user.id_usuario, nuevo_hash):
            flash("Contraseña actualizada.", "success")
        else:
            flash("No se pudo actualizar la contraseña.", "danger")
        return redirect(url_for("mi_cuenta"))

    return render_template("mi_cuenta.html", perfil_form=perfil_form, pwd_form=pwd_form)


# ----------------- Solicitudes de reposición ----------------- #
@app.route("/solicitudes", methods=["GET", "POST"])
@login_required
def solicitudes():
    form = SolicitudForm()
    if form.validate_on_submit():
        solicitud_service.crear(
            usuario_id=current_user.id_usuario,
            titulo=form.titulo.data,
            detalle=form.detalle.data,
        )
        flash("Solicitud enviada.", "success")
        return redirect(url_for("solicitudes"))
    lista = solicitud_service.listar_por_usuario(current_user.id_usuario)
    return render_template("solicitudes.html", form=form, solicitudes=lista)


@app.route("/admin/solicitudes", methods=["GET", "POST"])
@login_required
def admin_solicitudes():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores.", "danger")
        return redirect(url_for("index"))
    lista = solicitud_service.listar_todas()
    return render_template("admin_solicitudes.html", solicitudes=lista)


@app.route("/admin/solicitudes/<int:solicitud_id>/<string:estado>", methods=["POST"])
@login_required
def cambiar_estado_solicitud(solicitud_id, estado):
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores.", "danger")
        return redirect(url_for("index"))
    if estado not in ["aprobada", "rechazada", "pendiente"]:
        flash("Estado no valido.", "danger")
        return redirect(url_for("admin_solicitudes"))
    ok = solicitud_service.actualizar_estado(solicitud_id, estado)
    flash("Estado actualizado." if ok else "No se pudo actualizar.", "info" if ok else "danger")
    return redirect(url_for("admin_solicitudes"))


# ----------------- Exportaciones y reportes ----------------- #
@app.route("/export/productos/<string:formato>")
@login_required
def export_productos(formato):
    productos = [_producto_a_dict(p) for p in producto_service.listar()]
    if formato.lower() == "json":
        return Response(json.dumps(productos, ensure_ascii=False, indent=2), mimetype="application/json")
    if formato.lower() == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "nombre", "categoria", "cantidad", "precio", "proveedor"])
        writer.writeheader()
        writer.writerows(productos)
        csv_data = output.getvalue()
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=productos.csv"},
        )
    flash("Formato no soportado. Usa json o csv.", "danger")
    return redirect(url_for("inventario_view"))


def _csv_rows(path, headers):
    """Devuelve filas de un CSV si existe, sin levantar excepcion."""
    if not os.path.exists(path):
        return []
    rows = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append([r.get(h, "") for h in headers])
    except Exception:
        return []
    return rows


def _col_widths(headers, rows, max_width=520, min_col=60, max_col=200):
    """Calcula anchos aproximados segun longitud de texto para evitar solapamiento."""
    col_count = len(headers)
    lens = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            if idx >= col_count:
                break
            lens[idx] = max(lens[idx], len(str(cell)))
    widths = [min(max(min_col, l * 5), max_col) for l in lens]  # 5 px aprox por caracter
    total = sum(widths)
    if total > max_width:
        factor = max_width / total
        widths = [max(min_col, w * factor) for w in widths]
    return widths


def _pdf_table_response(title: str, headers, rows, filename: str, intro_lines=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    body_style = styles["Normal"].clone("BodySmall")
    body_style.fontSize = 9
    body_style.leading = 11
    body_style.wordWrap = "CJK"

    def _wrap(cell):
        # Numéricos directos, textos con Paragraph para wrap.
        if isinstance(cell, (int, float)):
            return cell
        return Paragraph(str(cell), body_style)

    wrapped_rows = [[_wrap(c) for c in row] for row in rows] if rows else [["—" for _ in headers]]

    data = [headers]
    data.extend(wrapped_rows)

    table = Table(data, colWidths=_col_widths(headers, rows))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (0, 1), (0, -1), "CENTER"),  # ID
                ("ALIGN", (-2, 1), (-2, -1), "CENTER"),  # Cantidad
                ("ALIGN", (-1, 1), (-1, -1), "LEFT"),  # Proveedor
                ("ALIGN", (-3, 1), (-3, -1), "RIGHT"),  # Precio
                ("ALIGN", (1, 1), (-4, -1), "LEFT"),  # Nombre/Categoria
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )

    intro = intro_lines or []
    elements = [Paragraph(title, styles["Heading1"]), Spacer(1, 12)]
    elements += [Paragraph(line, styles["Normal"]) for line in intro]
    elements.append(Spacer(1, 12))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")


@app.route("/reportes")
@login_required
def reportes_menu():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores.", "danger")
        return redirect(url_for("index"))
    return render_template("reportes/index.html")


@app.route("/reportes/productos/pdf")
@login_required
def reporte_productos_pdf():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores.", "danger")
        return redirect(url_for("index"))
    productos = producto_service.listar()
    rows = [[p.id, p.nombre, p.categoria, p.cantidad, f"${p.precio:,.2f}", p.proveedor] for p in productos]
    intro = [
        f"Total productos: {len(productos)}",
        f"Valor inventario: ${sum(p.precio * p.cantidad for p in productos):,.2f}",
    ]
    return _pdf_table_response(
        title="Reporte de Productos",
        headers=["ID", "Nombre", "Categoria", "Cant.", "Precio", "Proveedor"],
        rows=rows,
        filename="reporte_productos.pdf",
        intro_lines=intro,
    )


@app.route("/reportes/usuarios/pdf")
@login_required
def reporte_usuarios_pdf():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores.", "danger")
        return redirect(url_for("index"))
    usuarios = usuario_service.listar()
    rows = [[u.id_usuario, u.nombre, u.email, u.role] for u in usuarios]
    return _pdf_table_response(
        title="Reporte de Usuarios",
        headers=["ID", "Nombre", "Correo", "Rol"],
        rows=rows,
        filename="reporte_usuarios.pdf",
    )


@app.route("/reportes/facturas/pdf")
@login_required
def reporte_facturas_pdf():
    facturas = factura_service.listar()
    if facturas:
        rows = [
            [f.fecha.strftime("%Y-%m-%d"), f.numero, f.cliente, f.estado, f"${f.total:,.2f}"]
            for f in facturas
        ]
        headers = ["Fecha", "Factura", "Cliente", "Estado", "Total"]
    else:
        headers = ["fecha", "numero", "cliente", "total"]
        rows = _csv_rows(os.path.join(DATA_DIR, "facturas.csv"), headers)
        rows = [[r[0], r[1], r[2], r[3]] for r in rows]
        headers = ["Fecha", "Factura", "Cliente", "Total"]
    return _pdf_table_response(
        title="Reporte de Facturas",
        headers=headers,
        rows=rows,
        filename="reporte_facturas.pdf",
        intro_lines=["Fuente: data/facturas.csv."],
    )


@app.route("/reportes/solicitudes/pdf")
@login_required
def reporte_solicitudes_pdf():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores.", "danger")
        return redirect(url_for("index"))
    solicitudes = solicitud_service.listar_todas()
    rows = []
    for s in solicitudes:
        usuario = f"{s.usuario.nombre} ({s.usuario.email})" if s.usuario else "-"
        rows.append([s.id, usuario, s.titulo, s.detalle, s.estado])
    return _pdf_table_response(
        title="Reporte de Solicitudes",
        headers=["ID", "Usuario", "Título", "Detalle", "Estado"],
        rows=rows,
        filename="reporte_solicitudes.pdf",
    )


@app.route("/reportes/clientes/pdf")
@login_required
def reporte_clientes_pdf():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores.", "danger")
        return redirect(url_for("index"))
    clientes = cliente_service.listar()
    rows = [[c.ruc, c.nombre, c.telefono, c.email, c.direccion] for c in clientes]
    return _pdf_table_response(
        title="Reporte de Clientes",
        headers=["RUC", "Nombre", "Teléfono", "Correo", "Dirección"],
        rows=rows,
        filename="reporte_clientes.pdf",
    )



# ----------- Facturas (vista) ----------- #
@app.route("/facturas")
@login_required
def facturas_view():
    facturas = _facturas_con_totales()
    return render_template("facturas.html", facturas=facturas)


@app.route("/facturas/<int:factura_id>")
@login_required
def factura_detalle_view(factura_id):
    data = _factura_detalle_data(factura_id)
    if data is None:
        flash("Factura no encontrada.", "danger")
        return redirect(url_for("facturas_view"))
    return render_template(
        "factura_detalle.html",
        factura=data["factura"],
        detalles=data["detalles"],
        subtotal=data["subtotal"],
        iva=data["iva"],
        total=data["total"],
    )


# Helpers de facturas
def _facturas_con_totales():
    # aplica stock pendiente antes de mostrar
    factura_detalle_service.aplicar_stock_pendiente()
    resultados = []
    with SessionLocal() as session:
        facturas = (
            session.execute(
                select(Factura)
                .options(
                    selectinload(Factura.detalles).selectinload(FacturaDetalle.producto),
                    selectinload(Factura.cliente_obj),
                )
                .order_by(Factura.fecha.desc(), Factura.id.desc())
            )
            .scalars()
            .all()
        )
        changed = False
        for f in facturas:
            subtotal = sum((d.cantidad or 0) * (d.precio_unitario or 0) for d in f.detalles)
            iva = subtotal * 0.15
            total = subtotal + iva
            if abs((f.total or 0) - total) > 0.01:
                f.total = total
                changed = True
            resultados.append(
                {
                    "id": f.id,
                    "fecha": f.fecha,
                    "numero": f.numero,
                    "cliente": f.cliente,
                    "estado": f.estado,
                    "total": total,
                }
            )
        if changed:
            session.commit()
    return resultados


def _factura_detalle_data(factura_id: int):
    with SessionLocal() as session:
        factura = (
            session.execute(
                select(Factura)
                .options(
                    selectinload(Factura.detalles).selectinload(FacturaDetalle.producto),
                    selectinload(Factura.cliente_obj),
                )
                .where(Factura.id == factura_id)
            )
            .scalar_one_or_none()
        )
        if not factura:
            return None
        # Asegura stock aplicado para esta factura
        for d in factura.detalles:
            if d.producto and not d.stock_aplicado:
                d.producto.cantidad = max(0, (d.producto.cantidad or 0) - (d.cantidad or 0))
                d.stock_aplicado = True
        session.flush()

        detalles_data = []
        for d in factura.detalles:
            detalles_data.append(
                {
                    "concepto": d.producto.nombre if d.producto else "Producto eliminado",
                    "cantidad": d.cantidad,
                    "precio": d.precio_unitario,
                    "total": (d.cantidad or 0) * (d.precio_unitario or 0),
                }
            )
        subtotal = sum(item["total"] for item in detalles_data)
        iva = subtotal * 0.15
        total = subtotal + iva
        if abs((factura.total or 0) - total) > 0.01:
            factura.total = total
            session.commit()
        # Convert factura a dict ligero para templating
        cliente = factura.cliente_obj
        factura_data = {
            "id": factura.id,
            "numero": factura.numero,
            "fecha": factura.fecha,
            "cliente": factura.cliente,
            "estado": factura.estado,
            "cliente_ruc": cliente.ruc if cliente else "",
            "cliente_email": cliente.email if cliente else "",
            "cliente_tel": cliente.telefono if cliente else "",
            "cliente_dir": cliente.direccion if cliente else "",
        }
        return {"factura": factura_data, "detalles": detalles_data, "subtotal": subtotal, "iva": iva, "total": total}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
