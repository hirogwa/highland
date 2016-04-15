from highland import models


def create(user, show_id, title, description, audio_id):
    show = models.Show.query.\
        filter_by(owner_user_id=user.id, id=show_id).first()
    audio = models.Audio.query.\
        filter_by(owner_user_id=user.id, id=audio_id).first()

    assert show, 'No such show. (user,show)=({0},{1})'.format(user.id, show_id)
    assert audio,\
        'No such audio. (user,audio)=({0},{1})'.format(user.id, audio_id)

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


def delete(episode):
    models.db.session.delete(episode)
    models.db.session.commit()
    return True


def load(show):
    return models.Episode.query.\
        filter_by(owner_user_id=show.owner_user_id, show_id=show.id).\
        all()
