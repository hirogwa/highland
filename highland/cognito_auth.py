from Crypto.PublicKey import RSA
from functools import wraps
from flask import session
import base64
import datetime
import jwt
import pytz

from highland import app


class CognitoAuth:
    def __init__(self, cognito_jwt_set, cognito_region, cognito_user_pool_id):
        self.cognito_jwt_set = cognito_jwt_set
        self.cognito_region = cognito_region
        self.cognito_user_pool_id = cognito_user_pool_id
        self.unauthenticated = None
        self.username = ''

    def decode_access_token(self, token):
        kid = jwt.get_unverified_header(token).get('kid')
        jwt_set = [x for x in self.cognito_jwt_set.get('keys')
                   if x.get('kid') == kid][0]
        n_str, e_str = jwt_set.get('n'), jwt_set.get('e')

        # signature verification included
        decoded = jwt.decode(token, key=_public_key(n_str, e_str))

        if decoded.get('iss') != 'https://cognito-idp.{}.amazonaws.com/{}' \
                  .format(self.cognito_region, self.cognito_user_pool_id):
            app.logger.error('token invalid. bad iss.')
            raise ValueError()
        if decoded.get('token_use') != 'access':
            app.logger.error('token invalid. bad token_use.')
            raise ValueError()
        if datetime.datetime.fromtimestamp(decoded.get('exp'), pytz.utc) \
           < datetime.datetime.now(pytz.utc):
            app.logger.error('token invalid. expired.')
            raise ValueError()

        return decoded

    def require_authenticated(self, redirect=False):
        def decorator(func):
            @wraps(func)
            def token_checked(*args, **kwargs):
                try:
                    self._consume_token()
                except:
                    if redirect and self.unauthenticated:
                        return self.unauthenticated()
                    else:
                        return 'authentication required', 403
                return func(*args, **kwargs)
            return token_checked
        return decorator

    def unauthenticated_redirect(self, func):
        self.unauthenticated = func
        return func

    def user_loader(self, func):
        self.get_authenticated_user = func
        return func

    def authenticated_user(self):
        return self.get_authenticated_user(self.username)

    def _consume_token(self):
        if 'access_token' not in session:
            raise ValueError()
        token_decoded = self.decode_access_token(session['access_token'])
        self.username = token_decoded.get('username')


def _public_key(n_str, e_str):
    to_num = lambda x: int.from_bytes(
        base64.urlsafe_b64decode(_pad(x)), byteorder='big')
    pub = RSA.construct([to_num(x) for x in [n_str, e_str]])
    return pub.exportKey(format='PEM').decode('ascii')


def _pad(s):
    r = len(s) % 4
    return s + '=' * (4 - r) if r > 0 else s
