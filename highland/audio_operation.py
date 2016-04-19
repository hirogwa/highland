from highland import models, media_storage

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
