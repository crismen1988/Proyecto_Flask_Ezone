from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, Regexp


class ProductoForm(FlaskForm):
    nombre = StringField(
        "Nombre del Producto",
        validators=[DataRequired(message="El nombre es obligatorio"), Length(min=3, max=100)],
    )
    categoria = SelectField(
        "Categoría",
        choices=[
            ("Seguridad Electrónica", "Seguridad Electrónica"),
            ("Domótica", "Domótica"),
            ("Automatización", "Automatización"),
            ("Instalaciones Eléctricas", "Instalaciones Eléctricas"),
            ("Cámaras IP", "Cámaras IP"),
            ("Alarmas", "Alarmas"),
            ("Acceso Control", "Acceso Control"),
        ],
        validators=[DataRequired(message="Seleccione una categoría")],
    )
    cantidad = IntegerField(
        "Cantidad en stock",
        validators=[DataRequired(message="La cantidad es obligatoria"), NumberRange(min=0)],
    )
    precio = FloatField(
        "Precio unitario ($)",
        validators=[DataRequired(message="El precio es obligatorio"), NumberRange(min=0.01)],
    )
    proveedor = StringField("Proveedor", validators=[Length(max=100)])
    imagen_url = StringField(
        "URL de imagen (opcional)",
        validators=[Optional(), Regexp(r"^https?://.+", message="Ingrese una URL válida"), Length(max=255)],
    )
    imagen_archivo = FileField(
        "Subir imagen (opcional)",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif"], "Solo imágenes")],
    )
    enviar = SubmitField("Guardar Producto")


class BusquedaForm(FlaskForm):
    termino = StringField("Buscar producto...", validators=[Length(min=2, max=50)])
    categoria_filtro = SelectField(
        "Filtrar por categoría",
        choices=[
            ("todas", "Todas las categorías"),
            ("Seguridad Electrónica", "Seguridad Electrónica"),
            ("Domótica", "Domótica"),
            ("Automatización", "Automatización"),
            ("Instalaciones Eléctricas", "Instalaciones Eléctricas"),
            ("Cámaras IP", "Cámaras IP"),
            ("Alarmas", "Alarmas"),
            ("Acceso Control", "Acceso Control"),
        ],
    )
    buscar = SubmitField("Buscar")
