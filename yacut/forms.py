from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from .utils import (
    MAX_CUSTOM_ID_LENGTH,
    is_short_id_taken,
    is_valid_short_id,
)


class URLForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 256)],
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[Length(max=MAX_CUSTOM_ID_LENGTH), Optional()],
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if field.data:
            if not is_valid_short_id(field.data):
                raise ValidationError(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if is_short_id_taken(field.data):
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )


class FilesForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы',
        validators=[FileRequired(message='Обязательное поле')],
    )
    submit = SubmitField('Загрузить')
