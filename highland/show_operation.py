import datetime
import urllib.parse
from highland import models, app, common, exception


def create(user, title, description, subtitle, language, author, category,
           explicit, image_id, alias):
    if not common.is_valid_alias(alias):
        raise exception.InvalidValueError(
            'show alias not accepted. {}'.format(alias))

    show = models.Show(user, title, description, subtitle, language, author,
                       category, explicit, image_id, alias)
    models.db.session.add(show)
    models.db.session.commit()
    return show


def update(user, show_id, title, description, subtitle, language, author,
           category, explicit, image_id):
    show = get_show_or_assert(user, show_id)
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


def delete(show):
    models.db.session.delete(show)
    models.db.session.commit()
    return True


def load(user):
    return models.Show.query.filter_by(owner_user_id=user.id).all()


def get_show_or_assert(user, show_id):
    show = models.Show.query.filter_by(id=show_id).first()
    if not show:
        raise exception.NoSuchEntityError(
            'show does not exist. id:{}'.format(show_id))
    access_allowed_or_raise(user.id, show)
    return show


def get_show_url(show):
    return urllib.parse.urljoin(app.config.get('HOST_SITE'), show.alias)


def access_allowed_or_raise(user_id, show):
    if show.owner_user_id != user_id:
        raise exception.AccessNotAllowedError(
            'user:{}, show: {}'.format(user_id, show.id))
    return show
