DATABASE = 'postgresql+psycopg2://localhost:5432/highland'

S3_REGION = ''
S3_BUCKET_SITES = ''
S3_BUCKET_FEED = ''
S3_BUCKET_AUDIO = ''
S3_BUCKET_IMAGE = ''

COGNITO_REGION = ''
COGNITO_USER_POOL_ID = ''
COGNITO_CLIENT_ID = ''
COGNITO_IDENTITY_POOL_ID = ''
COGNITO_IDENTITY_PROVIDER = ''

# https://cognito-idp.COGNITO_REGION.amazonaws.com/COGNITO_USER_POOL_ID/.well-known/jwks.json
COGNITO_JWT_SET = {
    "keys": [{
        "alg": "",
        "e": "",
        "kid": "",
        "kty": "",
        "n": "",
        "use": ""
    }, {
        "alg": "",
        "e": "",
        "kid": "",
        "kty": "",
        "n": "",
        "use": ""
    }]
}

APP_SECRET = b''

HOST_SITE = ''
HOST_FEED = ''
HOST_AUDIO = ''
HOST_IMAGE = ''

HOST_OLYMPIA = ''
