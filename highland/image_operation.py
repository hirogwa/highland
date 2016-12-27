import imghdr
import os
import urllib.parse
import uuid
from highland import models, media_storage, settings, app, exception, common


def create(user, image_file):
    guid, type = store_image_data(user, image_file)
    image = models.Image(user, image_file.filename, guid, type)
    models.db.session.add(image)
    models.db.session.commit()
    return image


def delete(user, image_ids):
    for id in image_ids:
        image = get_image_or_assert(user, id)
        try:
            media_storage.delete(
                image.guid, settings.S3_BUCKET_IMAGE, user.username)
        except:
            app.logger.error(
                'Failed to delete media:({},{})'.format(
                    user.id, image.id), exc_info=1)
        else:
            models.db.session.delete(image)
    models.db.session.commit()
    return True


def load(user):
    return models.Image.query.filter_by(owner_user_id=user.id).all()


def get_image_or_assert(user, image_id):
    image = models.Image.query.\
        filter_by(owner_user_id=user.id, id=image_id).first()
    if not image:
        raise exception.NoSuchEntityError(
            'user:{}, image:{}'.format(user.id, image_id))
    access_allowed_or_raise(user.id, image)
    return image


def get_image_url(user, image):
    access_allowed_or_raise(user.id, image)
    return urllib.parse.urljoin(settings.HOST_IMAGE,
                                '{}/{}'.format(user.username, image.guid))


def store_image_data(user, image_file):
    temp_path_dir = user.username
    if not os.path.exists(temp_path_dir):
        os.mkdir(temp_path_dir)

    guid = uuid.uuid4().hex
    temp_path = os.path.join(temp_path_dir, guid)
    image_file.save(temp_path)

    type = imghdr.what(temp_path)
    common.require_true(
        type in ['jpeg', 'png'], 'image type not supported:{}'.format(type))

    image_data = open(temp_path, 'rb')
    media_storage.upload(
        image_data, settings.S3_BUCKET_IMAGE, guid,
        user.username, ContentType='image/{}'.format(type))

    os.remove(temp_path)
    return guid, type


def access_allowed_or_raise(user_id, image):
    if image.owner_user_id != user_id:
        raise exception.AccessNotAllowedError(
            'user:{}, audio: {}'.format(user_id, image.id))
    return image
