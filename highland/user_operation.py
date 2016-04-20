from highland import models


def signup(username, email, password):
    if models.User.query.filter_by(username=username).first():
        raise AssertionError('User exists: {}'.format(username))

    user = models.User(username, email, password)
    models.db.session.add(user)
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
