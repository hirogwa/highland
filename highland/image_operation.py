import urllib.parse
import uuid
from highland import app, media_operation, user_operation
from highland.common import verify_ownership
from highland.exception import NoSuchEntityError
from highland.models import db, Image


def create(user_id, file_name, file_type):
    """Creates an image. Intended to be called by front end."""

    guid = uuid.uuid4().hex
    image = Image(user_id, file_name, guid, file_type)
    db.session.add(image)
    db.session.commit()
    return dict(image)


def delete(user_id, image_ids):
    """Deletes the images.
    Intended to be called by front end.
    """
    return media_operation.delete(
        user_id=user_id, media_ids=image_ids, model_class=Image,
        get_key=_get_image_key, bucket=app.config.get('S3_BUCKET_IMAGE'))


def load(user_id):
    """Returns all the images owned by the user.
    Intended to be called by front end.
    """

    user = user_operation.get_model(user_id)
    q = Image.query.filter_by(owner_user_id=user_id)
    return [_add_attributes(user, image) for image in q.all()]


def get(user_id, image_id):
    """Returns the image as dict. Exception is raised if not found.
    Intended to be called by front end
    """
    image = verify_ownership(user_id, get_model(image_id))
    user = user_operation.get_model(image.owner_user_id)
    return _add_attributes(user, image)


def get_model(image_id):
    """Returns the image as the raw model. Exception is raised if not found.
    """
    image = Image.query.filter_by(id=image_id).first()
    if not image:
        raise NoSuchEntityError(
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
