import imghdr
import os
import urllib.parse
import uuid
from highland import models, media_storage, settings


def create(user, image_file):
    guid, type = store_image_data(user.id, image_file)
    image = models.Image(user, image_file.filename, guid, type)
    models.db.session.add(image)
    models.db.session.commit()
    return image


def delete(image):
    media_storage.delete(image.guid, settings.S3_BUCKET_IMAGE)
    models.db.session.delete(image)
    models.db.session.commit()
    return True


def load(user):
    return models.Image.query.filter_by(owner_user_id=user.id).all()


def get_image_or_assert(user, image_id):
    image = models.Image.query.\
        filter_by(owner_user_id=user.id, id=image_id).first()
    if image:
        return image
    else:
        raise AssertionError(
            'No such image. (user,image)={}{}'.format(user.id, image_id))


def get_image_url(image):
    # TODO
    return urllib.parse.urljoin(
        settings.HOST,
        'user/{}/image/{}.{}'.format(
            image.owner_user_id, image.guid,
            image.type.replace('jpeg', 'jpg')))


def store_image_data(user_id, image_file):
    temp_path_dir = str(user_id)
    if not os.path.exists(temp_path_dir):
        os.mkdir(temp_path_dir)

    guid = uuid.uuid4().hex
    temp_path = os.path.join(temp_path_dir, guid)
    image_file.save(temp_path)

    type = imghdr.what(temp_path)
    assert type in ['jpeg', 'png'], 'image type not supported:{}'.format(type)

    media_storage.upload(
        image_file, settings.S3_BUCKET_IMAGE,
        '{}.{}'.format(guid, type.replace('jpeg', 'jpg')),
        ContentType='image/{}'.format(type))

    os.remove(temp_path)
    return guid, type
