import imghdr
import os
import uuid
from highland import models, media_storage

IMAGE_FOLDER = 'image'


def create(user, image_file):
    guid, type = store_image_data(user.id, image_file)
    image = models.Image(user, image_file.filename, guid, type)
    models.db.session.add(image)
    models.db.session.commit()
    return image


def delete(image):
    media_storage.delete(image.guid, IMAGE_FOLDER)
    models.db.session.delete(image)
    models.db.session.commit()
    return True


def load(user):
    return models.Image.query.filter_by(owner_user_id=user.id).all()


def store_image_data(user_id, image_file):
    temp_path_dir = str(user_id)
    if not os.path.exists(temp_path_dir):
        os.mkdir(temp_path_dir)

    guid = uuid.uuid4().hex
    temp_path = os.path.join(temp_path_dir, guid)
    image_file.save(temp_path)

    type = imghdr.what(temp_path)
    assert type in ['jpeg', 'png'], 'image type not supported:{}'.format(type)

    media_storage.upload(image_file, '{}.{}'.format(guid, type), IMAGE_FOLDER,
                         ContentType='image/{}'.format(type))

    os.remove(temp_path)
    return guid, type
