import urllib.parse
import uuid
from highland import models, media_storage, app, exception, user_operation
from highland.models import Image, User


def create(user_id, file_name, file_type):
    """Creates an image. Intended to be called by front end."""

    guid = uuid.uuid4().hex
    image = models.Image(user_id, file_name, guid, file_type)
    models.db.session.add(image)
    models.db.session.commit()
    return dict(image)


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
    """Returns all the images owned by the user.
    Intended to be called by front end.
    """

    user = user_operation.get(user_id)
    q = models.Image.query.filter_by(owner_user_id=user_id)
    return [_add_attributes(user, image) for image in q.all()]


def get(image_id):
    """Returns the image as dict. Exception is raised if not found.
    Intended to be called by front end
    """
    image = get_model(image_id)
    user = user_operation.get(image.owner_user_id)
    return _add_attributes(user, image)


def get_model(image_id):
    """Returns the image as the raw model. Exception is raised if not found.
    """
    image = models.Image.query.filter_by(id=image_id).first()
    if not image:
        raise exception.NoSuchEntityError(
            'Image not found. Id:{}'.format(image_id))
    return image


def get_image_url(user, image):
    """Returns the url for the image."""

    return urllib.parse.urljoin(
        app.config.get('HOST_IMAGE'),
        urllib.parse.quote(_get_image_key(user, image)))


def _add_attributes(user, image):
    """Add attributes to the image entity before passing it to the client.
    Returns the image as a dict."""

    d = dict(image)
    d['url'] = get_image_url(user, image)
    return d


def _get_image_key(user, image):
    return '{}/{}'.format(user.identity_id, image.guid)
