import uuid
from highland import models, media_storage

IMAGE_FOLDER = 'image'


def create(user, image_file):
    guid = store_image_data(user.id, image_file)
    image = models.Image(user, image_file.filename, guid)
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
    guid = uuid.uuid4().hex
    media_storage.upload(image_file, guid, IMAGE_FOLDER)
    return guid
