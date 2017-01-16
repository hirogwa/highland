from highland import models, exception, settings
from highland.aws_resources import cognito_identity


def create(username, id_token):
    '''
    initiate new user. intended to be called at user's first login
    '''
    if models.User.query.filter_by(username=username).first():
        raise exception.OperationNotAllowedError(
            'User already exists: {}'.format(username))

    identity_id = cognito_identity.get_id(
        IdentityPoolId=settings.COGNITO_IDENTITY_POOL_ID,
        Logins={
            settings.COGNITO_IDENTITY_PROVIDER: id_token
        }).get('IdentityId')

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
        raise exception.NoSuchEntityError('user:{}'.format(id))
    return user


def get_or_assert(id):
    user = models.User.query.filter_by(id=id).first()
    if not user:
        raise exception.NoSuchEntityError('user:{}'.format(id))
    return user
