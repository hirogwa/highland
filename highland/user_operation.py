from highland import models


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
