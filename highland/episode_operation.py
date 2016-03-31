from highland import models


def create(show, title, description, audio):
    episode = models.Episode(show, title, description, audio)
    models.db.session.add(episode)
    models.db.session.commit()
    return episode
