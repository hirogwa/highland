import datetime
import urllib.parse
from highland import models, app, common, exception
from highland.common import verify_ownership
from highland.models import Show


def create(user_id, title, description, subtitle, language, author, category,
           explicit, image_id, alias):
    """Creates a show.
    Intended to be called by front end.
    """

    if not common.is_valid_alias(alias):
        raise exception.InvalidValueError(
            'show alias not accepted. {}'.format(alias))

    show = Show(user_id, title, description, subtitle, language, author,
                category, explicit, image_id, alias)
    models.db.session.add(show)
    models.db.session.commit()
    return dict(show)


def update(user_id, show_id, title, description, subtitle, language, author,
           category, explicit, image_id):
    """Updates the show. Exception is thrown if the show is not found.
    Intended to be called by front end.
    """

    show = verify_ownership(user_id, get_model(show_id))
    show.title = title
    show.description = description
    show.subtitle = subtitle
    show.language = language
    show.author = author
    show.category = category
    show.explicit = explicit
    show.image_id = image_id
    show.last_build_datetime = datetime.datetime.now(datetime.timezone.utc)
    models.db.session.commit()
    return dict(show)


def delete(user_id, show_id):
    """Deletes the show. Exception is thrown if the show is not found.
    Intended to be called by front end.
    """

    show = verify_ownership(user_id, get_model(show_id))
    models.db.session.delete(show)
    models.db.session.commit()
    return True


def load(user_id):
    """Loads all shows owned by the user.
    Intended to be called by front end.
    """

    shows = Show.query.filter_by(owner_user_id=user_id).all()
    return [dict(x) for x in shows]


def get(user_id, show_id):
    """Gets and returns the show as dict. Exception is raised if not found.
    Intended to be called by front end.
    """
    return dict(verify_ownership(user_id, get_model(show_id)))


def get_model(show_id):
    """Gets and returns the show as the raw model object."""

    show = Show.query.filter_by(id=show_id).first()
    if not show:
        raise exception.NoSuchEntityError(
            'Show does not exist. Id:{}'.format(show_id))
    show.url = urllib.parse.urljoin(app.config.get('HOST_SITE'), show.alias)
    return show
