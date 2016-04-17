from highland import models


def create(user, show_id, title, description, audio_id):
    show = get_show_or_assert(user, show_id)
    audio = get_audio_or_assert(user, audio_id)

    episode = models.Episode(show, title, description, audio)
    models.db.session.add(episode)
    models.db.session.commit()
    return episode


def update(user, show_id, episode_id, title, description, audio_id):
    get_show_or_assert(user, show_id)
    episode = get_episode_or_assert(user, show_id, episode_id)
    audio = get_audio_or_assert(user, audio_id)

    episode.title = title
    episode.description = description
    episode.audio_id = audio.id
    models.db.session.commit()
    return episode


def delete(episode):
    models.db.session.delete(episode)
    models.db.session.commit()
    return True


def load(user, show_id):
    show = get_show_or_assert(user, show_id)
    return models.Episode.query.\
        filter_by(owner_user_id=show.owner_user_id, show_id=show.id).\
        all()


def get_show_or_assert(user, show_id):
    show = models.Show.query.\
        filter_by(owner_user_id=user.id, id=show_id).first()
    if show:
        return show
    else:
        raise AssertionError(
            'No such show. (user,show):({0},{1})'.format(user.id, show_id))


def get_audio_or_assert(user, audio_id):
    audio = models.Audio.query.\
        filter_by(owner_user_id=user.id, id=audio_id).first()
    if audio:
        return audio
    else:
        raise AssertionError(
            'No such audio. (user,audio)=({0},{1})'.format(user.id, audio_id))


def get_episode_or_assert(user, show_id, episode_id):
    episode = models.Episode.query.\
        filter_by(owner_user_id=user.id,
                  show_id=show_id,
                  id=episode_id).first()
    if episode:
        return episode
    else:
        raise AssertionError(
            'No such episode. (user,show,episode)=({0},{1},{2})'.
            format(user.id, show_id, episode_id))
