from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo


class UsuarioForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[DataRequired(message="El nombre es obligatorio"), Length(min=3, max=100)],
    )
    email = StringField(
        "Correo",
        validators=[
            DataRequired(message="El correo es obligatorio"),
            Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Correo no válido"),
            Length(max=120),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria"), Length(min=6, max=255)],
    )
    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators=[DataRequired(message="Confirme la contraseña"), EqualTo("password", message="No coincide")],
    )
    enviar = SubmitField("Registrar Usuario")


class LoginForm(FlaskForm):
    email = StringField(
        "Correo",
        validators=[DataRequired(message="El correo es obligatorio"), Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")],
    )
    password = PasswordField("Contraseña", validators=[DataRequired(message="La contraseña es obligatoria")])
    enviar = SubmitField("Iniciar Sesion")


class ProfileForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[DataRequired(message="El nombre es obligatorio"), Length(min=3, max=100)],
    )
    email = StringField(
        "Correo",
        validators=[
            DataRequired(message="El correo es obligatorio"),
            Regexp(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", message="Correo no valido"),
            Length(max=120),
        ],
    )
    enviar = SubmitField("Guardar cambios")


class PasswordChangeForm(FlaskForm):
    password_actual = PasswordField("Contraseña actual", validators=[DataRequired(message="Ingresa tu contraseña actual")])
    password_nueva = PasswordField(
        "Nueva contraseña", validators=[DataRequired(message="Ingresa una nueva contraseña"), Length(min=6, max=255)]
    )
    password_confirmacion = PasswordField(
        "Confirmar nueva contraseña",
        validators=[DataRequired(message="Confirma la nueva contraseña"), EqualTo("password_nueva", message="No coincide")],
    )
    enviar = SubmitField("Actualizar contraseña")
