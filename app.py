from flask import Flask

app = Flask(__name__)

# Ruta principal: Presentación del negocio
@app.route('/')
def inicio():
    return """
    <h1>Bienvenidos a Ezone</h1>
    <p>Expertos en Seguridad Electrónica, Domótica e Instalaciones Eléctricas.</p>
    <hr>
    <small>Sistema de Gestión v1.0</small>
    """

# Ruta dinámica: Consulta de productos
@app.route('/producto/<nombre_producto>')
def producto(nombre_producto):
    # Usamos .replace("-", " ") para que si escribimos 'camara-ip' en la URL, se vea como 'camara ip'
    nombre_limpio = nombre_producto.replace("-", " ")
    
    return f"""
    <h3>Ezone - Consulta de Inventario</h3>
    <p>Producto: <strong>{nombre_limpio}</strong></p>
    <p>Estado: <span style="color: green;">Disponible en bodega</span></p>
    <a href="/">Volver al inicio</a>
    """

if __name__ == '__main__':
    app.run(debug=True)