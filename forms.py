# -*- coding: utf-8 -*-
"""
FORMS.PY - EZONE
Formularios con Flask-WTF
Incluye validaciones y proteccion CSRF
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    FloatField,
    IntegerField,
    SubmitField,
    SelectField,
    PasswordField,
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    Length,
    Optional,
    Regexp,
    EqualTo,
)


class ProductoForm(FlaskForm):
    """Formulario para agregar/editar productos."""

    nombre = StringField(
        "Nombre del Producto",
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=3, max=100, message="Entre 3 y 100 caracteres"),
        ],
    )

    categoria = SelectField(
        "Categoria",
        choices=[
            ("Seguridad Electrónica", "Seguridad Electrónica"),
            ("Domotica", "Domotica"),
            ("Automatizacion", "Automatizacion"),
            ("Instalaciones Electricas", "Instalaciones Electricas"),
            ("Camaras IP", "Camaras IP"),
            ("Alarmas", "Alarmas"),
            ("Acceso Control", "Acceso Control"),
        ],
        validators=[DataRequired(message="Seleccione una categoria")],
    )

    cantidad = IntegerField(
        "Cantidad en Stock",
        validators=[
            DataRequired(message="La cantidad es obligatoria"),
            NumberRange(min=0, message="No puede ser negativo"),
        ],
    )

    precio = FloatField(
        "Precio Unitario ($)",
        validators=[
            DataRequired(message="El precio es obligatorio"),
            NumberRange(min=0.01, message="Precio debe ser mayor a 0"),
        ],
    )

    proveedor = StringField(
        "Proveedor",
        validators=[Length(max=100, message="Maximo 100 caracteres")],
    )

    imagen_url = StringField(
        "URL de imagen (opcional)",
        validators=[
            Optional(),
            Regexp(r"^https?://.+", message="Ingrese una URL valida o deje vacio"),
            Length(max=255),
        ],
    )

    imagen_archivo = FileField(
        "Subir imagen (opcional)",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif"], "Solo imagenes")],
    )

    enviar = SubmitField("Guardar Producto")


class BusquedaForm(FlaskForm):
    termino = StringField(
        "Buscar producto...",
        validators=[Length(min=2, max=50, message="Entre 2 y 50 caracteres")],
    )

    categoria_filtro = SelectField(
        "Filtrar por categoria",
        choices=[
            ("todas", "Todas las categorias"),
            ("Seguridad Electrónica", "Seguridad Electrónica"),
            ("Domotica", "Domotica"),
            ("Automatizacion", "Automatizacion"),
            ("Instalaciones Electricas", "Instalaciones Electricas"),
            ("Camaras IP", "Camaras IP"),
            ("Alarmas", "Alarmas"),
            ("Acceso Control", "Acceso Control"),
        ],
    )

    buscar = SubmitField("Buscar")


class ClienteForm(FlaskForm):
    ruc = StringField(
        "RUC",
        validators=[
            DataRequired(message="El RUC es obligatorio"),
            Regexp(r"^\d{13}$", message="El RUC debe tener 13 digitos"),
        ],
    )

    nombre = StringField(
        "Nombre del Cliente",
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=3, max=100, message="Entre 3 y 100 caracteres"),
        ],
    )

    telefono = StringField(
        "Telefono",
        validators=[Optional(), Length(max=30, message="Maximo 30 caracteres")],
    )

    email = StringField(
        "Correo Electronico",
        validators=[
            Optional(),
            Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Correo no valido"),
            Length(max=120, message="Maximo 120 caracteres"),
        ],
    )

    direccion = StringField(
        "Direccion",
        validators=[Optional(), Length(max=200, message="Maximo 200 caracteres")],
    )

    enviar = SubmitField("Guardar Cliente")


class BusquedaClienteForm(FlaskForm):
    termino = StringField(
        "Buscar cliente...",
        validators=[Length(min=2, max=100, message="Entre 2 y 100 caracteres")],
    )

    buscar = SubmitField("Buscar")


class UsuarioForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=3, max=100, message="Entre 3 y 100 caracteres"),
        ],
    )

    email = StringField(
        "Correo",
        validators=[
            DataRequired(message="El correo es obligatorio"),
            Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Correo no valido"),
            Length(max=120, message="Maximo 120 caracteres"),
        ],
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria"),
            Length(min=6, max=255, message="Entre 6 y 255 caracteres"),
        ],
    )

    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators=[
            DataRequired(message="Confirme la contraseña"),
            EqualTo("password", message="Las contraseñas deben coincidir"),
        ],
    )

    enviar = SubmitField("Registrar Usuario")


class LoginForm(FlaskForm):
    email = StringField(
        "Correo",
        validators=[
            DataRequired(message="El correo es obligatorio"),
            Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Correo no valido"),
        ],
    )

    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria")],
    )

    enviar = SubmitField("Iniciar Sesion")


class ProfileForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=3, max=100, message="Entre 3 y 100 caracteres"),
        ],
    )
    email = StringField(
        "Correo",
        validators=[
            DataRequired(message="El correo es obligatorio"),
            Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Correo no valido"),
            Length(max=120, message="Maximo 120 caracteres"),
        ],
    )
    enviar = SubmitField("Guardar cambios")


class PasswordChangeForm(FlaskForm):
    password_actual = PasswordField(
        "Contraseña actual",
        validators=[DataRequired(message="Ingresa tu contraseña actual")],
    )
    password_nueva = PasswordField(
        "Nueva contraseña",
        validators=[
            DataRequired(message="Ingresa una nueva contraseña"),
            Length(min=6, max=255, message="Entre 6 y 255 caracteres"),
        ],
    )
    password_confirmacion = PasswordField(
        "Confirmar nueva contraseña",
        validators=[
            DataRequired(message="Confirma la nueva contraseña"),
            EqualTo("password_nueva", message="Las contraseñas deben coincidir"),
        ],
    )
    enviar = SubmitField("Actualizar contraseña")


class SolicitudForm(FlaskForm):
    titulo = StringField(
        "Titulo",
        validators=[
            DataRequired(message="El titulo es obligatorio"),
            Length(min=3, max=120, message="Entre 3 y 120 caracteres"),
        ],
    )
    detalle = StringField(
        "Detalle",
        validators=[
            DataRequired(message="Describe la necesidad"),
            Length(min=3, max=300, message="Entre 3 y 300 caracteres"),
        ],
    )
    enviar = SubmitField("Enviar solicitud")
