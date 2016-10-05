import re
import bleach


def is_valid_alias(alias):
    return alias is not None \
        and re.fullmatch('[a-zA-Z0-9_]+', alias) is not None


def clean_html(s):
    tags = bleach.ALLOWED_TAGS + ['br']
    return bleach.clean(s, tags=tags)
