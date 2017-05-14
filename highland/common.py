import re
import bleach

from highland.exception import AccessNotAllowedError, ValueError


def verify_ownership(user_id, entity):
    """Checks if the user with the given user_id owns the entity.
    Exception is raised if not.
    """
    if entity.owner_user_id == user_id:
        return entity
    else:
        raise AccessNotAllowedError


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
        raise ValueError(message)
    else:
        raise ValueError()
