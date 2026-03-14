"""
FORMS.PY - EZONE
Formularios con Flask-WTF
Incluye validaciones y protección CSRF
"""

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, Regexp


class ProductoForm(FlaskForm):
    """
    Formulario para agregar/editar productos de EZONE
    Incluye validaciones según el PDF:
    - DataRequired: Campos obligatorios
    - Length: Mínimo/máximo caracteres
    - NumberRange: Valores numéricos válidos
    """
    
    nombre = StringField(
        'Nombre del Producto',
        validators=[
            DataRequired(message="⚠️ El nombre es obligatorio"),
            Length(min=3, max=100, message="⚠️ Entre 3 y 100 caracteres")
        ]
    )
    
    categoria = SelectField(
        'Categoría',
        choices=[
            ('Seguridad Electrónica', 'Seguridad Electrónica'),
            ('Domótica', 'Domótica'),
            ('Automatización', 'Automatización'),
            ('Instalaciones Eléctricas', 'Instalaciones Eléctricas'),
            ('Cámaras IP', 'Cámaras IP'),
            ('Alarmas', 'Alarmas'),
            ('Acceso Control', 'Acceso Control')
        ],
        validators=[DataRequired(message="⚠️ Seleccione una categoría")]
    )
    
    cantidad = IntegerField(
        'Cantidad en Stock',
        validators=[
            DataRequired(message="⚠️ La cantidad es obligatoria"),
            NumberRange(min=0, message="⚠️ No puede ser negativo")
        ]
    )
    
    precio = FloatField(
        'Precio Unitario ($)',
        validators=[
            DataRequired(message="⚠️ El precio es obligatorio"),
            NumberRange(min=0.01, message="⚠️ Precio debe ser mayor a $0")
        ]
    )
    
    proveedor = StringField(
        'Proveedor',
        validators=[
            Length(max=100, message="⚠️ Máximo 100 caracteres")
        ]
    )
    
    enviar = SubmitField('Guardar Producto')


class BusquedaForm(FlaskForm):
    """
    Formulario para buscar productos en el inventario
    """
    
    termino = StringField(
        'Buscar producto...',
        validators=[
            Length(min=2, max=50, message="⚠️ Entre 2 y 50 caracteres")
        ]
    )
    
    categoria_filtro = SelectField(
        'Filtrar por categoría',
        choices=[
            ('todas', 'Todas las categorías'),
            ('Seguridad Electrónica', 'Seguridad Electrónica'),
            ('Domótica', 'Domótica'),
            ('Automatización', 'Automatización'),
            ('Instalaciones Eléctricas', 'Instalaciones Eléctricas'),
            ('Cámaras IP', 'Cámaras IP'),
            ('Alarmas', 'Alarmas'),
            ('Acceso Control', 'Acceso Control')
        ]
    )
    
    buscar = SubmitField('Buscar')


class ClienteForm(FlaskForm):
    """
    Formulario para registro de clientes.
    """

    ruc = StringField(
        'RUC',
        validators=[
            DataRequired(message="El RUC es obligatorio"),
            Regexp(r"^\d{13}$", message="El RUC debe tener 13 digitos")
        ]
    )

    nombre = StringField(
        'Nombre del Cliente',
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=3, max=100, message="Entre 3 y 100 caracteres")
        ]
    )

    telefono = StringField(
        'Telefono',
        validators=[
            Optional(),
            Length(max=30, message="Maximo 30 caracteres")
        ]
    )

    email = StringField(
        'Correo Electronico',
        validators=[
            Optional(),
            Regexp(
                r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                message="Correo no valido"
            ),
            Length(max=120, message="Maximo 120 caracteres")
        ]
    )

    direccion = StringField(
        'Direccion',
        validators=[
            Optional(),
            Length(max=200, message="Maximo 200 caracteres")
        ]
    )

    enviar = SubmitField('Guardar Cliente')


class BusquedaClienteForm(FlaskForm):
    """
    Formulario para buscar clientes por nombre o RUC.
    """

    termino = StringField(
        'Buscar cliente...',
        validators=[
            Length(min=2, max=100, message="Entre 2 y 100 caracteres")
        ]
    )

    buscar = SubmitField('Buscar')


class UsuarioForm(FlaskForm):
    """
    Formulario simple para la tabla usuarios (id_usuario, nombre, mail, password).
    """

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=3, max=100, message="Entre 3 y 100 caracteres"),
        ],
    )

    mail = StringField(
        "Correo",
        validators=[
            DataRequired(message="El correo es obligatorio"),
            Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Correo no valido"),
            Length(max=120, message="Maximo 120 caracteres"),
        ],
    )

    password = StringField(
        "Password (plaintext para demo)",
        validators=[
            DataRequired(message="La contraseña es obligatoria"),
            Length(min=4, max=255, message="Entre 4 y 255 caracteres"),
        ],
    )

    enviar = SubmitField("Guardar Usuario")
