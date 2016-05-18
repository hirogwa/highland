import os
import uuid
import urllib.parse
from mutagen.mp3 import MP3
from highland import models, media_storage, settings


def create(user, audio_file):
    guid, duration, length, type = store_audio_data(user.id, audio_file)
    audio = models.Audio(user, audio_file.filename, duration, length, type,
                         guid)
    models.db.session.add(audio)
    models.db.session.commit()
    return audio


def delete(audio):
    media_storage.delete(audio.guid, settings.S3_BUCKET_AUDIO)
    models.db.session.delete(audio)
    models.db.session.commit()
    return True


def load(user):
    return models.Audio.query.\
        filter_by(owner_user_id=user.id).\
        all()


def get_audio_or_assert(user, audio_id):
    audio = models.Audio.query.\
        filter_by(owner_user_id=user.id, id=audio_id).first()
    if audio:
        return audio
    else:
        raise AssertionError(
            'No such audio. (user,audio)=({0},{1})'.format(user.id, audio_id))


def get_audio_url(audio):
    # TODO
    return urllib.parse.urljoin(
        settings.HOST,
        'user/{}/audio/{}'.format(audio.owner_user_id, audio.id))


def store_audio_data(user_id, audio_file):
    temp_path_dir = str(user_id)
    if not os.path.exists(temp_path_dir):
        os.mkdir(temp_path_dir)

    guid = uuid.uuid4().hex
    temp_path = os.path.join(temp_path_dir, guid)
    audio_file.save(temp_path)

    type = 'audio/mpeg'
    audio_data = open(temp_path, 'rb')
    media_storage.upload(audio_data, settings.S3_BUCKET_AUDIO,  guid,
                         ContentType=type)
    d, l = MP3(temp_path).info.length, os.stat(temp_path).st_size

    os.remove(temp_path)
    return guid, d, l, type
