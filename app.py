"""
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