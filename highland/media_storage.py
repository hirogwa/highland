import os
from highland.aws_resources import s3


def upload(file_data, bucket, file_name=None, folder='', **kwargs):
    file_name = file_name or file_data.filename
    key_name = os.path.join(folder, file_name)
    s3.Bucket(bucket).\
        put_object(Key=key_name, Body=file_data, ACL='public-read', **kwargs)


def delete(filename, bucket, folder=''):
    key_name = os.path.join(folder, filename)
    s3.Object(bucket, key_name).delete()


def delete_folder(bucket, folder):
    bucket = s3.Bucket(bucket)
    for obj in bucket.objects.filter(Prefix='{}/'.format(folder)):
        s3.Object(bucket.name, obj.key).delete()
