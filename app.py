"""
<<<<<<< HEAD
APP.PY - EZONE
Aplicacion Flask para gestion de inventario, clientes y servicios.
"""

from flask import Flask, render_template, redirect, url_for, flash, request
from forms import ProductoForm, BusquedaForm, ClienteForm, BusquedaClienteForm
from models import Inventario

app = Flask(__name__)
app.config["SECRET_KEY"] = "ezone_clave_secreta_seguridad_2024"

inventario = Inventario()


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
        flash("Producto agregado correctamente.", "success")
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
        inventario.actualizar_producto(
            id_producto=id,
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            cantidad=form.cantidad.data,
            precio=form.precio.data,
            proveedor=form.proveedor.data,
        )
        flash("Producto actualizado correctamente.", "info")
        return redirect(url_for("inventario_view"))

    return render_template("editar_producto.html", form=form, id=id)


@app.route("/eliminar/<int:id>")
def eliminar(id):
    if inventario.eliminar_producto(id):
        flash("Producto eliminado.", "warning")
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

        flash("Cliente actualizado correctamente.", "info")
        return redirect(url_for("clientes"))

    return render_template("editar_cliente.html", form=form, cliente=cliente)


@app.route("/servicios")
def servicios():
    """
    Seccion de servicios (instalacion, venta y mantenimiento).
    """
    return render_template("servicios.html")


@app.errorhandler(404)
def error_404(_e):
    return render_template("index.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)

=======
Sistema de Gestión - E'zone
Seguridad Electrónica, Domótica e Instalaciones Eléctricas
Baños de Agua Santa, Ecuador
"""

from flask import Flask

app = Flask(__name__)


# =========================================
# PÁGINA DE INICIO
# =========================================
@app.route('/')
def inicio():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E'zone - Inicio</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 0;
            }
            
            .header {
                background-color: #e74c3c;
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                margin: 0;
                font-size: 2.5em;
            }
            
            .nav {
                background-color: #2c3e50;
                padding: 10px;
                text-align: center;
            }
            
            .nav a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }
            
            .nav a:hover {
                color: #f39c12;
            }
            
            .container {
                max-width: 800px;
                margin: 30px auto;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            h2 {
                color: #2c3e50;
                border-bottom: 2px solid #e74c3c;
                padding-bottom: 10px;
            }
            
            p {
                line-height: 1.6;
                margin: 15px 0;
            }
            
            .features {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                margin: 25px 0;
            }
            
            .feature {
                background-color: #f8f9fa;
                padding: 15px;
                margin: 10px;
                border-radius: 5px;
                width: 200px;
                text-align: center;
                border-left: 4px solid #3498db;
            }
            
            .btn {
                display: inline-block;
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px 5px;
            }
            
            .btn:hover {
                background-color: #c0392b;
            }
            
            .footer {
                text-align: center;
                margin-top: 30px;
                color: #7f8c8d;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ E'zone</h1>
            <p>Seguridad Electrónica • Domótica • Instalaciones Eléctricas</p>
        </div>
        
        <div class="nav">
            <a href="/">Inicio</a>
            <a href="/productos">Productos</a>
            <a href="/servicios">Servicios</a>
            <a href="/contacto">Contacto</a>
        </div>
        
        <div class="container">
            <h2>Bienvenidos a E'zone</h2>
            
            <p><strong>E'zone</strong> es tu aliado en soluciones de seguridad electrónica, 
            domótica e instalaciones eléctricas en <strong>Baños de Agua Santa, Ecuador</strong>. 
            Ofrecemos tecnología de calidad y servicio personalizado para proteger tu hogar 
            y negocio.</p>
            
            <div class="features">
                <div class="feature">
                    <h3>🛡️ Seguridad</h3>
                    <p>Cámaras, alarmas y control de accesos</p>
                </div>
                
                <div class="feature">
                    <h3>🏠 Domótica</h3>
                    <p>Automatización para el Hogar, Oficina y Negocio</p>
                </div>
                
                <div class="feature">
                    <h3>⚡ Eléctrica</h3>
                    <p>Instalaciones residenciales</p>
                </div>
            </div>
            
            <p>¡Contáctanos hoy para una cotización gratuita!</p>
            
            <a href="/productos" class="btn">Ver Productos</a>
            <a href="/servicios" class="btn">Nuestros Servicios</a>
        </div>
        
        <div class="footer">
            <p>Sistema de Gestión v1.0 • © 2026 E'zone • Baños de Agua Santa, Ecuador</p>
        </div>
    </body>
    </html>
    """


# =========================================
# CONSULTA DE PRODUCTO (RUTA DINÁMICA)
# =========================================
@app.route('/producto/<nombre_producto>')
def producto(nombre_producto):
    nombre_limpio = nombre_producto.replace("-", " ").title()
    
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E'zone - Producto</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 0;
            }
            
            .header {
                background-color: #e74c3c;
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .nav {
                background-color: #2c3e50;
                padding: 10px;
                text-align: center;
            }
            
            .nav a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }
            
            .nav a:hover {
                color: #f39c12;
            }
            
            .container {
                max-width: 600px;
                margin: 30px auto;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            h2 {
                color: #2c3e50;
            }
            
            .product-info {
                background-color: #f8f9fa;
                padding: 15px;
                margin: 15px 0;
                border-radius: 5px;
                border-left: 4px solid #27ae60;
            }
            
            .status {
                color: #27ae60;
                font-weight: bold;
            }
            
            .btn {
                display: inline-block;
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px 5px;
            }
            
            .btn:hover {
                background-color: #c0392b;
            }
            
            .footer {
                text-align: center;
                margin-top: 30px;
                color: #7f8c8d;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📦 Consulta de Producto</h1>
        </div>
        
        <div class="nav">
            <a href="/">Inicio</a>
            <a href="/productos">Productos</a>
            <a href="/servicios">Servicios</a>
        </div>
        
        <div class="container">
            <h2>""" + nombre_limpio + """</h2>
            
            <div class="product-info">
                <p><strong>Código:</strong> """ + nombre_producto.upper() + """</p>
                <p><strong>Estado:</strong> <span class="status">✅ Disponible</span></p>
                <p><strong>Categoría:</strong> Seguridad Electrónica</p>
                <p><strong>Stock:</strong> 10 unidades</p>
            </div>
            
            <p>Información actualizada al 15 de febrero de 2026</p>
            
            <a href="/productos" class="btn">Ver Todos</a>
            <a href="/" class="btn">Volver al Inicio</a>
        </div>
        
        <div class="footer">
            <p>E'zone • Baños de Agua Santa, Ecuador</p>
        </div>
    </body>
    </html>
    """


# =========================================
# LISTA DE PRODUCTOS
# =========================================
@app.route('/productos')
def lista_productos():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E'zone - Productos</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 0;
            }
            
            .header {
                background-color: #3498db;
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .nav {
                background-color: #2c3e50;
                padding: 10px;
                text-align: center;
            }
            
            .nav a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }
            
            .nav a:hover {
                color: #f39c12;
            }
            
            .container {
                max-width: 800px;
                margin: 30px auto;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            
            .product-list {
                list-style: none;
                padding: 0;
            }
            
            .product-item {
                background-color: #f8f9fa;
                padding: 12px;
                margin: 8px 0;
                border-radius: 5px;
                border-left: 3px solid #3498db;
            }
            
            .product-item a {
                color: #e74c3c;
                text-decoration: none;
                font-weight: bold;
            }
            
            .product-item a:hover {
                text-decoration: underline;
            }
            
            .btn {
                display: inline-block;
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
            
            .btn:hover {
                background-color: #c0392b;
            }
            
            .footer {
                text-align: center;
                margin-top: 30px;
                color: #7f8c8d;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📦 Productos Disponibles</h1>
        </div>
        
        <div class="nav">
            <a href="/">Inicio</a>
            <a href="/productos">Productos</a>
            <a href="/servicios">Servicios</a>
            <a href="/contacto">Contacto</a>
        </div>
        
        <div class="container">
            <h2>Catálogo de Productos</h2>
            
            <ul class="product-list">
                <li class="product-item">📹 <a href="/producto/camara-ip-hd">Cámara IP HD</a> - Vigilancia 1080p</li>
                <li class="product-item">🚨 <a href="/producto/alarma-inteligente">Alarma Inteligente</a> - Sistema completo</li>
                <li class="product-item">🚪 <a href="/producto/control-acceso">Control de Acceso</a> - Biométrico</li>
                <li class="product-item">📱 <a href="/producto/smart-home-kit">Smart Home Kit</a> - Automatización</li>
                <li class="product-item">💡 <a href="/producto/sensor-movimiento">Sensor Movimiento</a> - Detección</li>
                <li class="product-item">🔌 <a href="/producto/tomacorriente-inteligente">Toma Inteligente</a> - Control remoto</li>
                <li class="product-item">🔔 <a href="/producto/timbre-video">Video Portero</a> - Identificación</li>
                <li class="product-item">🔋 <a href="/producto/bateria-respaldo">Batería Respaldo</a> - UPS 1500VA</li>
            </ul>
            
            <p><strong>Nota:</strong> Todos los productos incluyen garantía y soporte técnico.</p>
            
            <a href="/" class="btn">Volver al Inicio</a>
        </div>
        
        <div class="footer">
            <p>E'zone • Baños de Agua Santa, Ecuador</p>
        </div>
    </body>
    </html>
    """


# =========================================
# SERVICIOS
# =========================================
@app.route('/servicios')
def servicios():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E'zone - Servicios</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 0;
            }
            
            .header {
                background-color: #9b59b6;
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .nav {
                background-color: #2c3e50;
                padding: 10px;
                text-align: center;
            }
            
            .nav a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }
            
            .nav a:hover {
                color: #f39c12;
            }
            
            .container {
                max-width: 800px;
                margin: 30px auto;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            h2 {
                color: #2c3e50;
                border-bottom: 2px solid #9b59b6;
                padding-bottom: 10px;
            }
            
            .service {
                background-color: #f8f9fa;
                padding: 15px;
                margin: 15px 0;
                border-radius: 5px;
                border-left: 4px solid #9b59b6;
            }
            
            .service h3 {
                color: #2c3e50;
                margin-top: 0;
            }
            
            .btn {
                display: inline-block;
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
            
            .btn:hover {
                background-color: #c0392b;
            }
            
            .footer {
                text-align: center;
                margin-top: 30px;
                color: #7f8c8d;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔧 Nuestros Servicios</h1>
        </div>
        
        <div class="nav">
            <a href="/">Inicio</a>
            <a href="/productos">Productos</a>
            <a href="/servicios">Servicios</a>
            <a href="/contacto">Contacto</a>
        </div>
        
        <div class="container">
            <h2>Soluciones Integrales en Baños de Agua Santa</h2>
            
            <div class="service">
                <h3>📹 Instalación de Cámaras de Seguridad</h3>
                <p>Sistemas de videovigilancia IP y analógicos para tu hogar o negocio.</p>
            </div>
            
            <div class="service">
                <h3>🏠 Domótica Residencial</h3>
                <p>Automatización de luces, cortinas y dispositivos desde tu smartphone.</p>
            </div>
            
            <div class="service">
                <h3>⚡ Instalaciones Eléctricas</h3>
                <p>Proyectos eléctricos residenciales e industriales con estándares de seguridad.</p>
            </div>
            
            <div class="service">
                <h3>🔐 Control de Acceso</h3>
                <p>Sistemas de seguridad con huella digital, tarjetas o códigos para tu propiedad.</p>
            </div>
            
            <p><strong>Todos nuestros servicios incluyen:</strong> visita técnica gratuita, 
            garantía de 12 meses y soporte técnico local en Baños de Agua Santa.</p>
            
            <a href="/contacto" class="btn">Solicitar Cotización</a>
            <a href="/" class="btn">Volver al Inicio</a>
        </div>
        
        <div class="footer">
            <p>E'zone • Baños de Agua Santa, Ecuador</p>
        </div>
    </body>
    </html>
    """


# =========================================
# CONTACTO (CON DATOS REALES)
# =========================================
@app.route('/contacto')
def contacto():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E'zone - Contacto</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 0;
            }
            
            .header {
                background-color: #f39c12;
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .nav {
                background-color: #2c3e50;
                padding: 10px;
                text-align: center;
            }
            
            .nav a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }
            
            .nav a:hover {
                color: #f39c12;
            }
            
            .container {
                max-width: 600px;
                margin: 30px auto;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            h2 {
                color: #2c3e50;
                border-bottom: 2px solid #f39c12;
                padding-bottom: 10px;
            }
            
            .contact-info {
                line-height: 2;
                margin: 20px 0;
                font-size: 1.1em;
            }
            
            .contact-info strong {
                color: #2c3e50;
            }
            
            .contact-item {
                display: flex;
                align-items: center;
                margin: 12px 0;
            }
            
            .contact-icon {
                background-color: #f39c12;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
                font-weight: bold;
            }
            
            .btn {
                display: inline-block;
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
            
            .btn:hover {
                background-color: #c0392b;
            }
            
            .footer {
                text-align: center;
                margin-top: 30px;
                color: #7f8c8d;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📞 Contáctanos</h1>
        </div>
        
        <div class="nav">
            <a href="/">Inicio</a>
            <a href="/productos">Productos</a>
            <a href="/servicios">Servicios</a>
            <a href="/contacto">Contacto</a>
        </div>
        
        <div class="container">
            <h2>Información de Contacto</h2>
            
            <div class="contact-info">
                <div class="contact-item">
                    <div class="contact-icon">📱</div>
                    <div><strong>Teléfono:</strong> +593 983 461 462</div>
                </div>
                
                <div class="contact-item">
                    <div class="contact-icon">📧</div>
                    <div><strong>Email:</strong> ezone@contacto.ec</div>
                </div>
                
                <div class="contact-item">
                    <div class="contact-icon">📍</div>
                    <div><strong>Dirección:</strong> Baños de Agua Santa, Ecuador</div>
                </div>
                
                <div class="contact-item">
                    <div class="contact-icon">🕒</div>
                    <div><strong>Horario:</strong> Lunes a Viernes, 8:00 - 17:00</div>
                </div>
            </div>
            
            <h3>¿En qué podemos ayudarte?</h3>
            <ul>
                <li>Solicitar cotización sin compromiso</li>
                <li>Consultar disponibilidad de productos</li>
                <li>Programar instalación o mantenimiento</li>
                <li>Soporte técnico para equipos instalados</li>
            </ul>
            
            <p style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <strong>💡 Tip:</strong> ¡Visítanos en Baños de Agua Santa para una 
                demostración gratuita de nuestros sistemas de seguridad y domótica!
            </p>
            
            <a href="/" class="btn">Volver al Inicio</a>
        </div>
        
        <div class="footer">
            <p>E'zone • Sistema de Gestión v1.0 • Baños de Agua Santa, Ecuador</p>
        </div>
    </body>
    </html>
    """


# =========================================
# EJECUCIÓN
# =========================================
if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 94f3a120bce33f827806db98b2c4c43f8106d19b
