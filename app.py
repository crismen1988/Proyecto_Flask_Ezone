"""
APP.PY - EZONE
Aplicacion Flask para gestion de inventario y clientes.
"""

import csv
import json
import os
import io
from uuid import uuid4

from flask import Flask, render_template, redirect, url_for, flash, request, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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
from models import Inventario, Usuario, Solicitud

app = Flask(__name__)
app.config["SECRET_KEY"] = "ezone_clave_secreta_seguridad_2024"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirigir a login si no es autenticado

@login_manager.user_loader
def load_user(user_id):
    # Abrir una sesion nueva para recuperar el usuario segun su id
    with inventario.Session() as session:
        return session.get(Usuario, int(user_id))

# Rutas de autenticación
@app.route('/register', methods=['GET', 'POST'])
def register():
    # No mostrar registro si ya estoy autenticado
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = UsuarioForm()
    if form.validate_on_submit():
        # Si soy el primer usuario, me convierto en admin
        user_count = inventario.contar_usuarios()
        role = "admin" if user_count == 0 else "user"
        
        hashed_password = generate_password_hash(form.password.data)
        nuevo = inventario.agregar_usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            password=hashed_password,
            role=role
        )
        if nuevo is None:
            flash("El correo ya existe. Usa uno diferente.", "danger")
        else:
            flash(f"Usuario registrado correctamente como {role}. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya inicié sesión, vuelvo al inicio
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = inventario.obtener_usuario_por_email(form.email.data)
        if user is None:
            flash('Correo o contraseña incorrectos.', 'danger')
        elif check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    # Cierro la sesión actual
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))

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
@login_required
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
@login_required
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
@login_required
def agregar():
    form = ProductoForm()

    if form.validate_on_submit():
        imagen_valor = None
        # Primero intento guardar una imagen subida; si no, tomo la URL opcional
        if form.imagen_archivo.data and form.imagen_archivo.data.filename:
            filename = secure_filename(form.imagen_archivo.data.filename)
            if filename:
                nombre_unico = f"{uuid4().hex}_{filename}"
                ruta_destino = os.path.join(app.config["UPLOAD_FOLDER"], nombre_unico)
                form.imagen_archivo.data.save(ruta_destino)
                imagen_valor = f"uploads/{nombre_unico}"
        elif form.imagen_url.data:
            imagen_valor = form.imagen_url.data.strip()

        inventario.agregar_producto(
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            cantidad=form.cantidad.data,
            precio=form.precio.data,
            proveedor=form.proveedor.data,
            imagen=imagen_valor,
        )
        sincronizar_archivos_desde_inventario()
        flash("Producto agregado y archivos TXT/JSON/CSV sincronizados.", "success")
        return redirect(url_for("inventario_view"))

    return render_template("agregar_producto.html", form=form)


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
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
            # Mostrar URL si la imagen es remota
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
        # Si no se envía nada, conserva la imagen actual
        if imagen_valor is None and 'producto' in locals() and producto:
            imagen_valor = producto.imagen

        actualizado = inventario.actualizar_producto(
            id_producto=id,
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            cantidad=form.cantidad.data,
            precio=form.precio.data,
            proveedor=form.proveedor.data,
            imagen=imagen_valor,
        )
        if actualizado:
            sincronizar_archivos_desde_inventario()
            flash("Producto actualizado y archivos sincronizados.", "info")
        else:
            flash("No se pudo actualizar el producto.", "danger")
        return redirect(url_for("inventario_view"))

    return render_template("editar_producto.html", form=form, id=id, producto=locals().get("producto"))


@app.route("/eliminar/<int:id>")
@login_required
def eliminar(id):
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden eliminar productos.", "danger")
        return redirect(url_for("inventario_view"))
    if inventario.eliminar_producto(id):
        sincronizar_archivos_desde_inventario()
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
            productos = inventario.buscar_por_nombre(termino)
        elif categoria != "todas":
            productos = inventario.obtener_por_categoria(categoria)
        else:
            productos = inventario.obtener_todos()

    return render_template("buscar_producto.html", form=form, productos=productos)


@app.route("/clientes", methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
def eliminar_cliente(ruc):
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden eliminar clientes.", "danger")
        return redirect(url_for("clientes"))
    if inventario.eliminar_cliente(ruc):
        sincronizar_archivos_desde_clientes()
        flash("Cliente eliminado.", "warning")
    else:
        flash("No se pudo eliminar el cliente.", "danger")
    return redirect(url_for("clientes"))


@app.route("/clientes/editar/<string:ruc>", methods=["GET", "POST"])
@login_required
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
@login_required
def usuarios():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden gestionar usuarios.", "danger")
        return redirect(url_for('index'))
    """
    CRUD básico para la tabla usuarios (MySQL/SQLite).
    """
    form = UsuarioForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        nuevo = inventario.agregar_usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            password=hashed_password,
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
@login_required
def eliminar_usuario(id_usuario):
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden gestionar usuarios.", "danger")
        return redirect(url_for('index'))
    if inventario.eliminar_usuario(id_usuario):
        flash("Usuario eliminado.", "warning")
    else:
        flash("No se pudo eliminar el usuario.", "danger")
    return redirect(url_for("usuarios"))


@app.route("/usuarios/editar/<int:id_usuario>", methods=["GET", "POST"])
@login_required
def editar_usuario(id_usuario):
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores pueden gestionar usuarios.", "danger")
        return redirect(url_for('index'))
    usuarios = inventario.obtener_usuarios()
    usuario = next((u for u in usuarios if u.id_usuario == id_usuario), None)
    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("usuarios"))

    form = UsuarioForm()

    if request.method == "GET":
        form.nombre.data = usuario.nombre
        form.email.data = usuario.email
    # No cargo la contraseña por seguridad

    if form.validate_on_submit():
        # Solo actualizo si me dan una contraseña nueva
        password = generate_password_hash(form.password.data) if form.password.data else usuario.password
        actualizado, motivo = inventario.actualizar_usuario(
            id_usuario=id_usuario,
            nombre=form.nombre.data,
            email=form.email.data,
            role=usuario.role,  # Mantengo el rol actual
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


# ----------------- Cuenta de usuario ----------------- #
@app.route("/mi_cuenta", methods=["GET", "POST"])
@login_required
def mi_cuenta():
    perfil_form = ProfileForm()
    pwd_form = PasswordChangeForm()

    # Aqui precargo mi nombre y correo en el formulario de perfil
    if request.method == "GET":
        perfil_form.nombre.data = current_user.nombre
        perfil_form.email.data = current_user.email

    if perfil_form.enviar.data and perfil_form.validate_on_submit():
        # Actualizo mis datos basicos
        actualizado, motivo = inventario.actualizar_usuario(
            id_usuario=current_user.id_usuario,
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
        # Verifico mi password actual antes de cambiarla
        if not check_password_hash(current_user.password, pwd_form.password_actual.data):
            flash("La contraseña actual es incorrecta.", "danger")
            return redirect(url_for("mi_cuenta"))
        nuevo_hash = generate_password_hash(pwd_form.password_nueva.data)
        if inventario.cambiar_password(current_user.id_usuario, nuevo_hash):
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
        # Creo mi solicitud de reposicion
        inventario.crear_solicitud(
            usuario_id=current_user.id_usuario,
            titulo=form.titulo.data,
            detalle=form.detalle.data,
        )
        flash("Solicitud enviada.", "success")
        return redirect(url_for("solicitudes"))
    lista = inventario.obtener_solicitudes_usuario(current_user.id_usuario)
    return render_template("solicitudes.html", form=form, solicitudes=lista)


@app.route("/admin/solicitudes", methods=["GET", "POST"])
@login_required
def admin_solicitudes():
    if not current_user.is_admin():
        flash("Acceso denegado. Solo administradores.", "danger")
        return redirect(url_for("index"))
    # Como admin veo todas las solicitudes
    lista = inventario.obtener_solicitudes()
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
    # Actualizo el estado seleccionado para la solicitud
    ok = inventario.actualizar_estado_solicitud(solicitud_id, estado)
    flash("Estado actualizado." if ok else "No se pudo actualizar.", "info" if ok else "danger")
    return redirect(url_for("admin_solicitudes"))


# ----------------- Exportación solo lectura ----------------- #
@app.route("/export/productos/<string:formato>")
@login_required
def export_productos(formato):
    productos = [_producto_a_dict(p) for p in inventario.obtener_todos()]
    if formato.lower() == "json":
        # Entrego el JSON directamente
        return Response(json.dumps(productos, ensure_ascii=False, indent=2), mimetype="application/json")
    if formato.lower() == "csv":
        # Genero CSV en memoria para descargar
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)


