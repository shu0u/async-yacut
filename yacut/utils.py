import random
import re
import string

from .models import URLMap

SHORT_ID_LENGTH = 6
MAX_CUSTOM_ID_LENGTH = 16
ALLOWED_CHARS = string.ascii_letters + string.digits
SHORT_ID_PATTERN = r'^[A-Za-z0-9]{1,16}$'
FORBIDDEN_SHORT = 'files'


def get_unique_short_id():
    while True:
        short_id = ''.join(
            random.choices(ALLOWED_CHARS, k=SHORT_ID_LENGTH)
        )
        if URLMap.query.filter_by(short=short_id).first() is None:
            return short_id


def is_valid_short_id(short_id):
    return bool(re.match(SHORT_ID_PATTERN, short_id))


def is_short_id_taken(short_id):
    if short_id == FORBIDDEN_SHORT:
        return True
    return URLMap.query.filter_by(short=short_id).first() is not None
