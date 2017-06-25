import uuid
import urllib.parse
from highland import app, media_operation, user_operation
from highland.exception import NoSuchEntityError
from highland.models import db, Audio, Episode


def create(user_id, file_name, duration, length, file_type):
    """Creates a new audio entity, owned by the specified user.
    Intended to be called by front end.
    """

    guid = uuid.uuid4().hex
    audio = Audio(user_id, file_name, duration, length, file_type, guid)
    db.session.add(audio)
    db.session.commit()
    return dict(audio)


def delete(user_id, audio_ids):
    """Deletes the audios.
    Intended to be called by front end.
    """
    return media_operation.delete(
        user_id=user_id, media_ids=audio_ids, model_class=Audio,
        get_key=_get_audio_key, bucket=app.config.get('S3_BUCKET_AUDIO'))


def load(user_id, unused_only=False, whitelisted_id=None):
    """Returns sequence of the audios owned by the user.
    Intended to be called by front end.
    """

    audio_query = db.session. \
        query(Audio, Episode). \
        outerjoin(Episode). \
        filter(Audio.owner_user_id == user_id)

    if unused_only:
        episodes_with_audio_reserved = Episode.query. \
            filter_by(owner_user_id=user_id). \
            filter(Episode.audio_id.isnot(None)). \
            filter(Episode.audio_id != whitelisted_id) .\
            all()
        black_list = (e.audio_id for e in episodes_with_audio_reserved)
        audio_query = audio_query.filter(Audio.id.notin_(black_list))

    def _dict_with_episode(user, audio, episode):
        d = dict(audio)
        d['url'] = get_audio_url(user, audio)
        d['show_id'] = episode.show_id if episode else None
        d['episode_id'] = episode.id if episode else None
        d['episode_title'] = episode.title if episode else None
        return d

    user = user_operation.get_model(id=user_id)
    return [_dict_with_episode(user, a, e) for a, e in audio_query.all()]


def get(audio_id):
    """Retrieves audio. Exception is raised if not found."""

    audio = Audio.query.filter_by(id=audio_id).first()
    if not audio:
        raise NoSuchEntityError(
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
