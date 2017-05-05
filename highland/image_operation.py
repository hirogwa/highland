import urllib.parse
import uuid
from highland import models, media_storage, app, exception


def create(user, file_name, file_type):
    guid = uuid.uuid4().hex
    image = models.Image(user, file_name, guid, file_type)
    models.db.session.add(image)
    models.db.session.commit()
    return image


def delete(user, image_ids):
    for id in image_ids:
        image = get(id)
        try:
            media_storage.delete(
                _get_image_key(user, image), app.config.get('S3_BUCKET_IMAGE'))
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


def get(image_id):
    """Retrieves image. Exception is raised if not found."""
    image = models.Image.query.filter_by(id=image_id).first()
    if not image:
        raise exception.NoSuchEntityError(
            'Image not found. Id:{}'.format(image_id))
    return image


def get_image_url(user, image):
    access_allowed_or_raise(user.id, image)
    return urllib.parse.urljoin(
        app.config.get('HOST_IMAGE'),
        urllib.parse.quote(_get_image_key(user, image)))


def access_allowed_or_raise(user_id, image):
    if image.owner_user_id != user_id:
        raise exception.AccessNotAllowedError(
            'user:{}, audio: {}'.format(user_id, image.id))
    return image


def _get_image_key(user, image):
    return '{}/{}'.format(user.identity_id, image.guid)
