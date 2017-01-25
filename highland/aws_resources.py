import boto3
from highland import app

s3 = boto3.resource(
    's3',
    region_name=app.config.get('S3_REGION'),
    aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
)

cognito_idp = boto3.client(
    'cognito-idp',
    aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
)

cognito_identity = boto3.client(
    'cognito-identity',
    aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
)
