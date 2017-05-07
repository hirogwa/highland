from highland import models, exception


def create(username, identity_id):
    """Initiate new user. intended to be called at user's first login.
    """
    if models.User.query.filter_by(username=username).first():
        raise exception.OperationNotAllowedError(
            'User already exists: {}'.format(username))

    user = models.User(username, username, identity_id)
    models.db.session.add(user)
    models.db.session.commit()
    return user


def update(id, username, name):
    """Updates the user. Exception is raised if no such user is found."""
    user = models.User.query.filter_by(id=id).first()
    if not user:
        raise exception.NoSuchEntityError('user:{}'.format(id))

    user.username = username
    user.name = name
    models.db.session.commit()
    return user


def get(id=None, username=None):
    """Retrieves user by id or username.

    Either id or username is required. If provided, both keys are used.
    If no such user is found, an exception is raised.
    """

    if not username and not id:
        raise ValueError('Either username or id is required')

    q = models.User.query
    if id:
        q = q.filter_by(id=id)
    if username:
        q = q.filter_by(username=username)
    user = q.first()

    if not user:
        raise exception.NoSuchEntityError(
            'No such user. username:{}, id:{}'.format(username, id))
    return user
