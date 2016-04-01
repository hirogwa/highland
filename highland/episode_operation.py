from highland import models


def create(show, title, description, audio):
    episode = models.Episode(show, title, description, audio)
    models.db.session.add(episode)
    models.db.session.commit()
    return episode


def update(episode, title, description, audio):
    episode.title = title
    episode.description = description
    episode.audio_id = audio.id
    models.db.session.commit()
    return episode
