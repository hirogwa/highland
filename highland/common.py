import re
import bleach

from highland import exception


def is_valid_alias(alias):
    return alias is not None \
        and re.fullmatch('[a-zA-Z0-9_]+', alias) is not None


def clean_html(s):
    tags = bleach.ALLOWED_TAGS + ['br']
    return bleach.clean(s, tags=tags)


def require_true(expression, message=None):
    if expression:
        return expression
    if message:
        raise exception.ValueError(message)
    else:
        raise exception.ValueError()
