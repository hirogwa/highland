import os
import uuid
import urllib.parse
from mutagen.mp3 import MP3
from highland import models, media_storage, settings, app, exception


def create(user, audio_file):
    guid, duration, length, type = store_audio_data(user, audio_file)
    audio = models.Audio(user, audio_file.filename, duration, length, type,
                         guid)
    models.db.session.add(audio)
    models.db.session.commit()
    return audio


def delete(user, audio_ids):
    for id in audio_ids:
        audio = get_audio_or_assert(user, id)
        try:
            media_storage.delete(
                audio.guid, settings.S3_BUCKET_AUDIO, user.username)
        except:
            app.logger.error(
                'Failed to delete media:({},{})'.format(
                    user.id, audio.id), exc_info=1)
        models.db.session.delete(audio)
    models.db.session.commit()
    return True


def load(user, unused_only=False, whitelisted_id=None):
    audios = models.Audio.query.\
        filter_by(owner_user_id=user.id).\
        all()

    episodes = models.Episode.query.\
        filter_by(owner_user_id=user.id).\
        all()

    if unused_only:
        black_list = \
            [x.audio_id for x in episodes if x.audio_id is not whitelisted_id]
        audios = [x for x in audios if x.id not in black_list]

    a_to_e = {e.audio_id: e for e in episodes}

    def _dict(audio):
        d = dict(audio)
        d['url'] = get_audio_url(user, audio)
        e = a_to_e.get(audio.id)
        d['show_id'] = e.show_id if e else None
        d['episode_id'] = e.id if e else None
        d['episode_title'] = e.title if e else None
        return d

    return [_dict(x) for x in audios]


def get_audio_or_assert(user, audio_id):
    audio = models.Audio.query.\
        filter_by(owner_user_id=user.id, id=audio_id).first()
    if not audio:
        raise exception.NoSuchEntityError(
            'user:{}, audio:{}'.format(user.id, audio_id))
    access_allowed_or_raise(user.id, audio)
    return audio


def get_audio_url(user, audio):
    access_allowed_or_raise(user.id, audio)
    return urllib.parse.urljoin(settings.HOST_AUDIO,
                                '{}/{}'.format(user.username, audio.guid))


def store_audio_data(user, audio_file):
    temp_path_dir = user.username
    if not os.path.exists(temp_path_dir):
        os.mkdir(temp_path_dir)

    guid = uuid.uuid4().hex
    temp_path = os.path.join(temp_path_dir, guid)
    audio_file.save(temp_path)

    type = 'audio/mpeg'
    audio_data = open(temp_path, 'rb')
    media_storage.upload(audio_data, settings.S3_BUCKET_AUDIO, guid,
                         user.username, ContentType=type)
    d, l = MP3(temp_path).info.length, os.stat(temp_path).st_size

    os.remove(temp_path)
    return guid, d, l, type


def access_allowed_or_raise(user_id, audio):
    if audio.owner_user_id != user_id:
        raise exception.AccessNotAllowedError(
            'user:{}, audio: {}'.format(user_id, audio.id))
    return audio
