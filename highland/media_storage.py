import boto3
import os
from highland import settings

s3 = boto3.resource(
    's3',
    region_name=settings.S3_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


def upload(file_data, file_name=None, folder='', **kwargs):
    file_name = file_name or file_data.filename
    key_name = os.path.join(folder, file_name)
    s3.Bucket(settings.S3_BUCKET).\
        put_object(Key=key_name, Body=file_data, ACL='public-read', **kwargs)


def delete(filename, folder=''):
    key_name = os.path.join(folder, filename)
    s3.Object(settings.S3_BUCKET, key_name).delete()
