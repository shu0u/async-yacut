import re

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from .models import URLMap

SHORT_ID_PATTERN = r'^[A-Za-z0-9]{1,16}$'
FORBIDDEN_SHORT = 'files'


class URLForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 256)],
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[Length(max=16), Optional()],
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if field.data:
            if not re.match(SHORT_ID_PATTERN, field.data):
                raise ValidationError(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if field.data == FORBIDDEN_SHORT:
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            if URLMap.query.filter_by(short=field.data).first() is not None:
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )


class FilesForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы',
        validators=[FileRequired(message='Обязательное поле')],
    )
    submit = SubmitField('Загрузить')