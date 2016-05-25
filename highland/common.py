import re


def is_valid_alias(alias):
    return re.fullmatch('[a-zA-Z0-9_]+', alias) is not None
