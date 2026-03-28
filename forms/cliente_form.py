from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class ClienteForm(FlaskForm):
    ruc = StringField(
        "RUC",
        validators=[DataRequired(message="El RUC es obligatorio"), Regexp(r"^\d{13}$", message="13 dígitos")],
    )
    nombre = StringField(
        "Nombre del Cliente",
        validators=[DataRequired(message="El nombre es obligatorio"), Length(min=3, max=100)],
    )
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=30)])
    email = StringField(
        "Correo electrónico",
        validators=[Optional(), Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Correo no válido"), Length(max=120)],
    )
    direccion = StringField("Dirección", validators=[Optional(), Length(max=200)])
    enviar = SubmitField("Guardar Cliente")


class BusquedaClienteForm(FlaskForm):
    termino = StringField("Buscar cliente...", validators=[Length(min=2, max=100)])
    buscar = SubmitField("Buscar")
