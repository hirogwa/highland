import boto3
from highland import app

s3 = boto3.resource('s3', region_name=app.config.get('S3_REGION'))
cognito_idp = boto3.client('cognito-idp')
cognito_identity = boto3.client('cognito-identity')
