from highland import models, exception


def create(username, identity_id):
    '''
    initiate new user. intended to be called at user's first login
    '''
    if models.User.query.filter_by(username=username).first():
        raise exception.OperationNotAllowedError(
            'User already exists: {}'.format(username))

    user = models.User(username, username, identity_id)
    models.db.session.add(user)
    models.db.session.commit()
    return user


def update(id, username, name):
    user = models.User.query.filter_by(id=id).first()
    if not user:
        raise exception.NoSuchEntityError('user:{}'.format(id))

    user.username = username
    user.name = name
    models.db.session.commit()
    return user


def get(username):
    user = models.User.query.filter_by(username=username).first()
    if not user:
        raise exception.NoSuchEntityError('user:{}'.format(username))
    return user


def get_or_assert(id):
    user = models.User.query.filter_by(id=id).first()
    if not user:
        raise exception.NoSuchEntityError('user:{}'.format(id))
    return user
