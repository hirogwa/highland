import hashlib
from highland import models, settings


def create(username, email, password):
    if models.User.query.filter_by(username=username).first():
        raise AssertionError('User exists: {}'.format(username))

    user = models.User(username, email, _hash(password))
    models.db.session.add(user)
    models.db.session.commit()
    return user


def update(id, username, email, password):
    user = models.User.query.filter_by(id=id).first()
    assert user, 'no such user ({})'.format(id)

    user.username = username
    user.email = email
    user.password = password
    models.db.session.commit()
    return user


def get(id=None, username=None, password=None):
    if id:
        user = models.User.query.filter_by(id=id).first()
        assert user, 'no user exists with the passed id'
        return user

    if username and password:
        user = models.User.query.\
            filter_by(username=username, password=password).first()
        assert user, 'no user exists with the passed credentials'
        return user

    raise ValueError('Not enough information supplied to find a user')


def _salt(s):
    return '{}{}'.format(settings.FIXED_SALT_STRING, s)


def _stretch(s):
    result = s
    for i in range(settings.STRETCH_COUNT):
        result = hashlib.sha256(result.encode(settings.ENCODING)).hexdigest()
    return result


def _hash(s):
    return _stretch(_salt(s))
