import datetime
import urllib.parse
from highland import models, show_operation, settings, audio_operation,\
    image_operation, common


def create(user, show_id, draft_status, alias, audio_id, image_id,
           scheduled_datetime=None, title='', subtitle='', description='',
           explicit=False):
    draft_status = models.Episode.DraftStatus(draft_status).name
    show = show_operation.get_show_or_assert(user, show_id)
    episode = set_default_value(user, models.Episode(
        show, title, subtitle, description, audio_id, draft_status,
        scheduled_datetime, explicit, image_id, alias))
    episode = valid_or_assert(user, episode)
    if episode.draft_status == models.Episode.DraftStatus.published.name:
        episode.published_datetime = \
            datetime.datetime.now(datetime.timezone.utc)

    models.db.session.add(episode)
    models.db.session.commit()

    _update_show_build_datetime(user, episode)
    return episode


def update(user, show_id, episode_id, draft_status, alias, audio_id, image_id,
           scheduled_datetime=None, title='', subtitle='', description='',
           explicit=False):
    show_operation.get_show_or_assert(user, show_id)
    episode = get_episode_or_assert(user, show_id, episode_id)

    episode.title = title
    episode.subtitle = subtitle
    episode.description = description
    episode.audio_id = audio_id
    episode.explicit = explicit
    episode.image_id = image_id
    episode.alias = alias
    episode.draft_status = models.Episode.DraftStatus(draft_status).name
    episode.scheduled_datetime = scheduled_datetime
    if episode.draft_status == models.Episode.DraftStatus.published.name:
        episode.published_datetime = \
            datetime.datetime.now(datetime.timezone.utc)
    if episode.draft_status == models.Episode.DraftStatus.draft.name:
        episode.published_datetime = None

    set_default_value(user, episode)
    valid_or_assert(user, episode)
    models.db.session.commit()

    _update_show_build_datetime(user, episode)
    return episode


def delete(user, show_id, episode_ids):
    for id in episode_ids:
        episode = get_episode_or_assert(user, show_id, id)
        models.db.session.delete(episode)
    models.db.session.commit()
    _update_show_build_datetime(user, episode)
    return True


def load(user, show_id, **kwargs):
    show = show_operation.get_show_or_assert(user, show_id)
    return models.Episode.query.\
        filter_by(owner_user_id=show.owner_user_id, show_id=show.id, **kwargs).\
        order_by(models.Episode.published_datetime.desc()).\
        all()


def load_with_audio(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    return models.db.session. \
        query(
            models.Episode,
            models.Audio). \
        join(
            models.Audio). \
        filter(
            models.Episode.owner_user_id == show.owner_user_id,
            models.Episode.show_id == show.id). \
        all()


def load_public(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    return models.Episode.query.\
        filter_by(owner_user_id=show.owner_user_id, show_id=show.id,
                  draft_status=models.Episode.DraftStatus.published.name).\
        order_by(models.Episode.published_datetime.desc()).\
        all()


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


def set_default_value(user, episode):
    if episode.alias is None or len(episode.alias) < 1:
        episode.alias = get_default_alias(user, episode.show_id)
    return episode


def valid_or_assert(user, episode):
    assert common.is_valid_alias(episode.alias), \
        'bad alias:{}'.format(episode.alias)

    if episode.audio_id is not None:
        audio_operation.get_audio_or_assert(user, episode.audio_id)
    if episode.image_id is not None:
        image_operation.get_image_or_assert(user, episode.image_id)

    if episode.draft_status != models.Episode.DraftStatus.draft.name:
        assert episode.title, 'title required'
        assert episode.description, 'description required'
        assert episode.audio_id, 'audio required'

    if episode.draft_status == models.Episode.DraftStatus.scheduled.name:
        assert episode.scheduled_datetime, 'scheduled_datetime required'
    else:
        episode.scheduled_datetime = None

    return episode


def get_episode_url(user, episode, show=None):
    if not show:
        show = show_operation.get_show_or_assert(user, episode.show_id)
    return urllib.parse.urljoin(
        settings.HOST_SITE, '{}/{}'.format(show.alias, episode.alias))


def get_preview_episode(user, show, title, subtitle, description, audio_id,
                        image_id):
    episode = models.Episode(show, title, subtitle, description, audio_id,
                             models.Episode.DraftStatus.published.name,
                             None, False, image_id, '_preview')
    episode.published_datetime = datetime.datetime.now(datetime.timezone.utc)
    return episode


def get_default_alias(user, show_id):
    q = models.db.session. \
        query(models.Episode.alias). \
        filter(models.Episode.owner_user_id == user.id and
               models.Episode.show_id == show_id)
    existing_aliases = [a for a, in q.all()]

    candidate = len(existing_aliases) + 1
    while str(candidate) in existing_aliases:
        candidate += 1

    return str(candidate)


def _update_show_build_datetime(user, episode):
    if episode.draft_status != models.Episode.DraftStatus.published.name:
        return None

    show = show_operation.get_show_or_assert(user, episode.show_id)
    show.last_build_datetime = datetime.datetime.now(datetime.timezone.utc)
    models.db.session.commit()
    return show
