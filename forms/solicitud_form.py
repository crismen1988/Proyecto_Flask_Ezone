from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class SolicitudForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(message="El título es obligatorio"), Length(min=3, max=120)])
    detalle = StringField(
        "Detalle", validators=[DataRequired(message="Describe la necesidad"), Length(min=3, max=300)]
    )
    enviar = SubmitField("Enviar solicitud")
