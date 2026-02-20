"""
Sistema de Gestión - E'zone
Seguridad Electrónica, Domótica e Instalaciones Eléctricas
Baños de Agua Santa, Ecuador
"""

from flask import Flask, render_template

app = Flask(__name__)


# =========================================
# PÁGINA DE INICIO
# =========================================
@app.route('/')
def inicio():
    return render_template('index.html')
       

# =========================================
# CONSULTA DE PRODUCTO
# =========================================
@app.route('/producto/<nombre_producto>')
def producto(nombre_producto):
    nombre_limpio = nombre_producto.replace("-"," ").title() 
    return render_template('detalle_producto.html', 
                           nombre_limpio=nombre_limpio, 
                           codigo=nombre_producto.upper())


# =========================================
# LISTA DE PRODUCTOS
# =========================================
@app.route('/productos')
def lista_productos():
    return render_template('productos.html')

# =========================================
# SERVICIOS
# =========================================
@app.route('/servicios')
def servicios():         
    return render_template('servicios.html')

# =========================================
# CONTACTO
# =========================================
@app.route('/contacto')
def contacto():     
    return render_template('contacto.html')

# =========================================
# EJECUCIÓN
# =========================================
if __name__ == '__main__':
    app.run(debug=True)