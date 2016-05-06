import urllib.parse
from highland import models, show_operation, settings


def create(user, show_id, draft_status, scheduled_datetime=None,
           title='', description='', audio_id=-1):
    draft_status = models.Episode.DraftStatus(draft_status)
    show = show_operation.get_show_or_assert(user, show_id)
    episode = valid_or_assert(user, models.Episode(
        show, title, description, audio_id, draft_status, scheduled_datetime))
    models.db.session.add(episode)
    models.db.session.commit()
    return episode


def update(user, show_id, episode_id, draft_status, scheduled_datetime=None,
           title='', description='', audio_id=-1):
    show_operation.get_show_or_assert(user, show_id)
    episode = get_episode_or_assert(user, show_id, episode_id)

    episode.title = title
    episode.description = description
    episode.audio_id = audio_id
    episode.draft_status = models.Episode.DraftStatus(draft_status)
    episode.scheduled_datetime = scheduled_datetime
    valid_or_assert(user, episode)
    models.db.session.commit()
    return episode


def delete(episode):
    models.db.session.delete(episode)
    models.db.session.commit()
    return True


def load(user, show_id, **kwargs):
    show = show_operation.get_show_or_assert(user, show_id)
    return models.Episode.query.\
        filter_by(owner_user_id=show.owner_user_id, show_id=show.id, **kwargs).\
        all()


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


def valid_or_assert(user, episode):
    if episode.draft_status != models.Episode.DraftStatus.draft:
        assert episode.title, 'title required'
        assert episode.description, 'description required'
        get_audio_or_assert(user, episode.audio_id)

    if episode.draft_status == models.Episode.DraftStatus.scheduled:
        assert episode.scheduled_datetime, 'scheduled_datetime required'
    else:
        episode.scheduled_datetime = None

    return episode


def get_episode_url(episode):
    # TODO
    return urllib.parse.urljoin(
        settings.HOST,
        'user/{}/show/{}'.format(episode.owner_user_id, episode.show_id))
