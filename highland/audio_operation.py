from highland import models


def create(user, audio_file):
    audio = models.Audio(user, audio_file)
    models.db.session.add(audio)
    models.db.session.commit()
    return audio
