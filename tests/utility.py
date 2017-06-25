"""Test utils"""

from highland.models import User


def create_user(id):
    user = User('username', 'name', 'identity')
    user.id = id
    return user


def assign_ids(entities, base):
    for x in entities:
        x.id = base
        base += 1
    return entities
