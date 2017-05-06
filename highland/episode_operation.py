import datetime
import urllib.parse
from highland import models, show_operation, app, audio_operation,\
    image_operation, common, exception
from highland.models import Episode


def create(show_id, draft_status, alias, audio_id, image_id,
           scheduled_datetime=None, title='', subtitle='', description='',
           explicit=False):
    """Creates a new episode under the specified show.
    If corresponding show does not exist, exception is raised.
    """

    draft_status = Episode.DraftStatus(draft_status).name
    # check if corresponding show exists
    show = show_operation.get(show_id)
    episode = Episode(
        show.id, show.owner_user_id, title, subtitle, description, audio_id,
        draft_status, scheduled_datetime, explicit, image_id, alias)
    _autofill_attributes(episode)
    _valid_or_assert(episode)

    models.db.session.add(episode)
    models.db.session.commit()

    _update_show_build_datetime(episode)
    return episode


def update(episode_id, draft_status=None, alias=None, audio_id=None,
           image_id=None, scheduled_datetime=None, title=None, subtitle=None,
           description=None, explicit=None):
    """Updates the episode.
    Exception is raised if the episode with the given id does not exist."""
    episode = get(episode_id)

    name_value_pairs = [
        ('title', title),
        ('subtitle', subtitle),
        ('description', description),
        ('audio_id', audio_id),
        ('explicit', explicit),
        ('image_id', image_id),
        ('alias', alias),
        ('draft_status', Episode.DraftStatus(draft_status).name),
        ('scheduled_datetime', scheduled_datetime)
    ]
    for name, value in [(x, y) for x, y in name_value_pairs]:
        setattr(episode, name, value)

    _autofill_attributes(episode)
    _valid_or_assert(episode)
    models.db.session.commit()

    _update_show_build_datetime(episode)
    return episode


def get(episode_id):
    """Retrieves the episode. Exception is raised if not found."""

    episode = Episode.query.filter_by(id=episode_id).first()
    if not episode:
        raise exception.NoSuchEntityError(
            'episode does not exist. id:{}'.format(episode_id))
    return episode


def delete(episode_ids):
    """Deletes episodes.
    If no episode exists for the passed id, exception is raised."""

    for episode in (get(id) for id in episode_ids):
        models.db.session.delete(episode)
    models.db.session.commit()
    _update_show_build_datetime(episode)
    return True


def load(show_id):
    """Retrieves all the episodes under the show."""

    show = show_operation.get(show_id)
    return Episode.query. \
        filter_by(show_id=show.id). \
        order_by(Episode.published_datetime.desc()). \
        all()


def load_with_audio(show_id):
    """Retrieves all the episodes, along with the associated audio."""

    show = show_operation.get(show_id)
    return models.db.session. \
        query(Episode, models.Audio). \
        join(models.Audio). \
        filter(Episode.show_id == show.id). \
        all()


def load_public(show_id):
    """Retrieves all the public episodes under the show."""

    show = show_operation.get(show_id)
    return Episode.query.\
        filter_by(show_id=show.id,
                  draft_status=Episode.DraftStatus.published.name).\
        order_by(Episode.published_datetime.desc()).\
        all()


def load_publish_target():
    return Episode.query. \
        filter_by(
            draft_status=Episode.DraftStatus.scheduled.name). \
        order_by(
            Episode.owner_user_id,
            Episode.show_id,
            Episode.id). \
        all()


def publish(episode):
    if episode.draft_status == Episode.DraftStatus.published.name:
        app.logger.warning(
            'Operation ignored. Episode already published:(show:{},id:{})'
            .format(episode.show_id, episode.id))
        return episode

    episode.draft_status = Episode.DraftStatus.published.name
    episode.published_datetime = datetime.datetime.now(datetime.timezone.utc)
    models.db.session.commit()
    return episode


def get_episode_url(episode, show=None):
    """Returns the url for the episode page"""

    show = show or show_operation.get(episode.show_id)
    return urllib.parse.urljoin(
        app.config.get('HOST_SITE'), '{}/{}'.format(show.alias, episode.alias))


def get_preview_episode(show, title, subtitle, description, audio_id,
                        image_id):
    """Creates temporary episode instance for a preview"""
    episode = Episode(
        show.id, show.owner_user_id, title, subtitle, description, audio_id,
        Episode.DraftStatus.published.name, None, False, image_id, '_preview')
    episode.published_datetime = datetime.datetime.now(datetime.timezone.utc)
    return episode


def get_default_alias(show_id):
    q = models.db.session. \
        query(Episode.alias). \
        filter(Episode.show_id == show_id)
    existing_aliases = [a for a, in q.all()]

    candidate = len(existing_aliases) + 1
    while str(candidate) in existing_aliases:
        candidate += 1

    return str(candidate)


def _valid_or_assert(episode):
    if not common.is_valid_alias(episode.alias):
        raise exception.InvalidValueError(
            'episode alias not accepted. {}'.format(episode.alias))

    if episode.audio_id is not None:
        audio_operation.get(episode.audio_id)
    if episode.image_id is not None:
        image_operation.get(episode.image_id)

    if episode.draft_status != Episode.DraftStatus.draft.name:
        common.require_true(episode.title, 'title required')
        common.require_true(episode.description, 'description required')
        common.require_true(episode.audio_id, 'audio required')

    if episode.draft_status == Episode.DraftStatus.scheduled.name:
        common.require_true(
            episode.scheduled_datetime, 'scheduled_datetime required')

    return episode


def _update_show_build_datetime(episode):
    if episode.draft_status != Episode.DraftStatus.published.name:
        return None

    show = show_operation.get(episode.show_id)
    show.last_build_datetime = datetime.datetime.now(datetime.timezone.utc)
    models.db.session.commit()
    return show


def _autofill_attributes(episode):
    if not episode.alias:
        episode.alias = get_default_alias(episode.show_id)

    episode.published_datetime = \
        PUBLISHED_DATETIME_FUNC[episode.draft_status]()

    episode.scheduled_datetime = \
        SCHEDULED_DATETIME_FUNC[episode.draft_status](episode)

    return episode


PUBLISHED_DATETIME_FUNC = {
    Episode.DraftStatus.published.name: lambda: datetime.datetime.now(
        datetime.timezone.utc),
    Episode.DraftStatus.draft.name: lambda: None,
    Episode.DraftStatus.scheduled.name: lambda: None
}

SCHEDULED_DATETIME_FUNC = {
    Episode.DraftStatus.published.name: lambda ep: None,
    Episode.DraftStatus.draft.name: lambda ep: None,
    Episode.DraftStatus.scheduled.name: lambda ep: ep.scheduled_datetime
}
