import uuid
import urllib.parse
from highland import models, media_storage, app, exception


def create(user, file_name, duration, length, file_type):
    guid = uuid.uuid4().hex
    audio = models.Audio(user, file_name, duration, length, file_type, guid)
    models.db.session.add(audio)
    models.db.session.commit()
    return audio


def delete(user, audio_ids):
    for id in audio_ids:
        audio = get_audio_or_assert(user, id)
        try:
            media_storage.delete(
                _get_audio_key(user, audio), app.config.get('S3_BUCKET_AUDIO'))
        except:
            app.logger.error(
                'Failed to delete media:({},{})'.format(
                    user.id, audio.id), exc_info=1)
        else:
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
            [x.audio_id for x in episodes if x.audio_id != whitelisted_id]
        audios = [x for x in audios if x.id not in black_list]

    a_to_e = {e.audio_id: e for e in episodes}

    def _dict_with_episode(user, audio, episode):
        d = dict(audio)
        d['url'] = get_audio_url(user, audio)
        d['show_id'] = episode.show_id if episode else None
        d['episode_id'] = episode.id if episode else None
        d['episode_title'] = episode.title if episode else None
        return d

    return [_dict_with_episode(user, x, a_to_e.get(x.id)) for x in audios]


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
    return urllib.parse.urljoin(
        app.config.get('HOST_AUDIO'),
        urllib.parse.quote(_get_audio_key(user, audio)))


def access_allowed_or_raise(user_id, audio):
    if audio.owner_user_id != user_id:
        raise exception.AccessNotAllowedError(
            'user:{}, audio: {}'.format(user_id, audio.id))
    return audio


def _get_audio_key(user, audio):
    return '{}/{}'.format(user.identity_id, audio.guid)
