import urllib.parse
from highland import models, media_storage, settings

AUDIO_FOLDER = 'audio'


def create(user, audio_file):
    media_storage.upload(audio_file, AUDIO_FOLDER)
    audio = models.Audio(user, audio_file.filename)
    models.db.session.add(audio)
    models.db.session.commit()
    return audio


def delete(audio):
    media_storage.delete(audio.filename, AUDIO_FOLDER)
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
