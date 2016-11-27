from highland import models


def create(username, email, name):
    if models.User.query.filter_by(username=username).first():
        raise AssertionError('User exists: {}'.format(username))

    user = models.User(username, email, name)
    models.db.session.add(user)
    models.db.session.commit()
    return user


def update(id, username, email, name):
    user = models.User.query.filter_by(id=id).first()
    assert user, 'no such user ({})'.format(id)

    user.username = username
    user.email = email
    user.name = name
    models.db.session.commit()
    return user


def get(username):
    user = models.User.query.filter_by(username=username).first()
    assert user, 'no such user. {}'.format(username)
    return user
