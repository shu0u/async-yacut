import random
import string

from .models import URLMap

SHORT_ID_LENGTH = 6
ALLOWED_CHARS = string.ascii_letters + string.digits


def get_unique_short_id():

    while True:
        short_id = ''.join(
            random.choices(ALLOWED_CHARS, k=SHORT_ID_LENGTH)
        )
        if URLMap.query.filter_by(short=short_id).first() is None:
            return short_id
