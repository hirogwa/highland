from Crypto.PublicKey import RSA
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


def _public_key(n_str, e_str):
    to_num = lambda x: int.from_bytes(
        base64.urlsafe_b64decode(_pad(x)), byteorder='big')
    pub = RSA.construct([to_num(x) for x in [n_str, e_str]])
    return pub.exportKey(format='PEM').decode('ascii')


def _pad(s):
    r = len(s) % 4
    return s + '=' * (4 - r) if r > 0 else s
