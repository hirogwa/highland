import uuid
import urllib.parse
from highland import models, media_storage, app, exception, user_operation


def create(user_id, file_name, duration, length, file_type):
    """Creates a new audio entity, owned by the specified user"""
    guid = uuid.uuid4().hex
    audio = models.Audio(user_id, file_name, duration, length, file_type, guid)
    models.db.session.add(audio)
    models.db.session.commit()
    return audio


def delete(user, audio_ids):
    for id in audio_ids:
        audio = get(id)
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


def load(user_id, unused_only=False, whitelisted_id=None):
    """Returns sequence of the audios owned by the user"""
    audios = models.Audio.query.\
        filter_by(owner_user_id=user_id).\
        all()

    episodes = models.Episode.query.\
        filter_by(owner_user_id=user_id).\
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

    user = user_operation.get(id=user_id)
    return [_dict_with_episode(user, x, a_to_e.get(x.id)) for x in audios]


def get(audio_id):
    """Retrieves audio. Exception is raised if not found."""

    audio = models.Audio.query.filter_by(id=audio_id).first()
    if not audio:
        raise exception.NoSuchEntityError(
            'Audio not found. Id:{}'.format(audio_id))
    return audio


def get_audio_url(user, audio):
    if user.id != audio.owner_user_id:
        raise ValueError(
            'Audio {} is owned by user {} but {} was given'.format(
                audio.id, audio.owner_user_id, user.id))
    return urllib.parse.urljoin(
        app.config.get('HOST_AUDIO'),
        urllib.parse.quote(_get_audio_key(user, audio)))


def _get_audio_key(user, audio):
    return '{}/{}'.format(user.identity_id, audio.guid)
