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
