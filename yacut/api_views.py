import re

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id

SHORT_ID_PATTERN = r'^[A-Za-z0-9]{1,16}$'
FORBIDDEN_SHORT = 'files'


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    custom_id = data.get('custom_id')
    if custom_id:
        if not re.match(SHORT_ID_PATTERN, custom_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if custom_id == FORBIDDEN_SHORT:
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
        if URLMap.query.filter_by(short=custom_id).first() is not None:
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
    else:
        custom_id = get_unique_short_id()

    url_map = URLMap(
        original=data['url'],
        short=custom_id,
    )
    db.session.add(url_map)
    db.session.commit()

    return jsonify({
        'url': url_map.original,
        'short_link': request.host_url + url_map.short,
    }), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), 200
