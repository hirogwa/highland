import urllib.parse
import uuid
from highland import models, media_storage, settings, app, exception


def create(user, file_name, file_type):
    guid = uuid.uuid4().hex
    image = models.Image(user, file_name, guid, file_type)
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
    return urllib.parse.urljoin(
        settings.HOST_MEDIA,
        '{}/image/{}'.format(urllib.parse.quote(user.identity_id), image.guid))


def access_allowed_or_raise(user_id, image):
    if image.owner_user_id != user_id:
        raise exception.AccessNotAllowedError(
            'user:{}, audio: {}'.format(user_id, image.id))
    return image
