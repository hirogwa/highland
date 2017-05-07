import datetime
import urllib.parse
from highland import models, app, common, exception


def create(user_id, title, description, subtitle, language, author, category,
           explicit, image_id, alias):
    """Creates a show."""

    if not common.is_valid_alias(alias):
        raise exception.InvalidValueError(
            'show alias not accepted. {}'.format(alias))

    show = models.Show(user_id, title, description, subtitle, language, author,
                       category, explicit, image_id, alias)
    models.db.session.add(show)
    models.db.session.commit()
    return show


def update(show_id, title, description, subtitle, language, author,
           category, explicit, image_id):
    """Updates the show. Exception is thrown if the show is not found."""

    show = get(show_id)
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
    return show


def delete(show_id):
    """Deletes the show. Exception is thrown if the show is not found."""

    show = get(show_id)
    models.db.session.delete(show)
    models.db.session.commit()
    return True


def load(user_id):
    """Loads all shows owned by the user."""

    return models.Show.query.filter_by(owner_user_id=user_id).all()


def get(show_id):
    """Retrieves the show. Exception is raised if not found."""

    show = models.Show.query.filter_by(id=show_id).first()
    if not show:
        raise exception.NoSuchEntityError(
            'Show does not exist. Id:{}'.format(show_id))
    show.url = urllib.parse.urljoin(app.config.get('HOST_SITE'), show.alias)
    return show
