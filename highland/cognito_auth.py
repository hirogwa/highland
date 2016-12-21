from Crypto.PublicKey import RSA
from functools import wraps
from flask import request, session
import base64
import datetime
import jwt
import pytz

from highland import app, exception


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
            raise exception.AuthError('token invalid. bad iss.')
        if decoded.get('token_use') != 'access':
            raise exception.AuthError('token invalid. bad token_use.')
        if datetime.datetime.fromtimestamp(decoded.get('exp'), pytz.utc) \
           < datetime.datetime.now(pytz.utc):
            raise exception.AuthError('token invalid. expired.')

        return decoded

    def require_authenticated(self, fallback=False, page=False):
        def decorator(func):
            @wraps(func)
            def token_checked(*args, **kwargs):
                try:
                    self._consume_token()
                except:
                    if page and self.refresh_token_attempt:
                        return self.load_refresh_token()
                    if fallback and self.unauthenticated:
                        return self.unauthenticated()
                    return 'authentication required', 403
                return func(*args, **kwargs)
            return token_checked
        return decorator

    def refresh_token_attempt(self, func):
        self.load_refresh_token = func
        return func

    def unauthenticated_redirect(self, func):
        self.unauthenticated = func
        return func

    def user_loader(self, func):
        self.get_authenticated_user = func
        return func

    @property
    def authenticated_user(self):
        return self.get_authenticated_user(self.username)

    @property
    def authenticated(self):
        try:
            self._consume_token()
        except:
            return False
        else:
            return True

    def login(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if request.method != 'POST':
                return func(*args, **kwargs)

            access_token = request.get_json().get('access_token')
            try:
                token_decoded = self.decode_access_token(access_token)
                self.username = token_decoded.get('username')
            except:
                return 'Invalid token', 400
            else:
                session['access_token'] = access_token
                return func(*args, **kwargs)
        return decorator

    def logout(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            session.pop('access_token', None)
            return func(*args, **kwargs)
        return decorator

    def _consume_token(self):
        if 'access_token' not in session:
            raise exception.AuthError('access token not in session')
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
