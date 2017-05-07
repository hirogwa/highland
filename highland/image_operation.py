import urllib.parse
import uuid
from highland import models, media_storage, app, exception
from highland.models import Image, User


def create(user_id, file_name, file_type):
    """Creates an image."""

    guid = uuid.uuid4().hex
    image = models.Image(user_id, file_name, guid, file_type)
    models.db.session.add(image)
    models.db.session.commit()
    return image


def delete(image_ids):
    """Deletes the images."""

    targets = models.db.session. \
        query(Image, User). \
        join(User). \
        filter(Image.id.in_(image_ids)). \
        order_by(Image.owner_user_id). \
        all()

    for image, user in targets:
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


def load(user_id):
    """Returns all the images owned by the user."""
    return models.Image.query.filter_by(owner_user_id=user_id).all()


def get(image_id):
    """Retrieves image. Exception is raised if not found."""
    image = models.Image.query.filter_by(id=image_id).first()
    if not image:
        raise exception.NoSuchEntityError(
            'Image not found. Id:{}'.format(image_id))
    return image


def get_image_url(user, image):
    return urllib.parse.urljoin(
        app.config.get('HOST_IMAGE'),
        urllib.parse.quote(_get_image_key(user, image)))


def _get_image_key(user, image):
    return '{}/{}'.format(user.identity_id, image.guid)
