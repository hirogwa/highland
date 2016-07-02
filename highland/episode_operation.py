import datetime
import urllib.parse
from highland import models, show_operation, settings, audio_operation,\
    image_operation, common


def create(user, show_id, draft_status, alias, scheduled_datetime=None,
           title='', subtitle='', description='', audio_id=-1, explicit=False,
           image_id=-1):
    if not common.is_valid_alias(alias):
        raise ValueError('alias not accepted. {}'.format(alias))

    draft_status = models.Episode.DraftStatus(draft_status).name
    show = show_operation.get_show_or_assert(user, show_id)
    episode = valid_or_assert(user, models.Episode(
        show, title, subtitle, description, audio_id, draft_status,
        scheduled_datetime, explicit, image_id, alias))
    if episode.draft_status == models.Episode.DraftStatus.published.name:
        episode.published_datetime = \
            datetime.datetime.now(datetime.timezone.utc)

    models.db.session.add(episode)
    models.db.session.commit()

    _update_show_build_datetime(user, episode)
    return episode


def update(user, show_id, episode_id, draft_status, alias,
           scheduled_datetime=None, title='', subtitle='', description='',
           audio_id=-1, explicit=False, image_id=-1):
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


def valid_or_assert(user, episode):
    if episode.audio_id > 0:
        audio_operation.get_audio_or_assert(user, episode.audio_id)
    if episode.image_id > 0:
        image_operation.get_image_or_assert(user, episode.image_id)

    if episode.draft_status != models.Episode.DraftStatus.draft:
        assert episode.title, 'title required'
        assert episode.description, 'description required'
        assert episode.audio_id > 0, 'audio required'

    if episode.draft_status == models.Episode.DraftStatus.scheduled:
        assert episode.scheduled_datetime, 'scheduled_datetime required'
    else:
        episode.scheduled_datetime = None

    return episode


def get_episode_url(user, episode, show=None):
    if not show:
        show = show_operation.get_show_or_assert(user, episode.show_id)
    return urllib.parse.urljoin(
        settings.HOST_SITE, '{}/{}'.format(show.alias, episode.alias))


def _update_show_build_datetime(user, episode):
    if episode.draft_status != models.Episode.DraftStatus.published.name:
        return None

    show = show_operation.get_show_or_assert(user, episode.show_id)
    show.last_build_datetime = datetime.datetime.now(datetime.timezone.utc)
    models.db.session.commit()
    return show
