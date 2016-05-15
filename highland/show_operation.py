import datetime
import urllib.parse
from highland import models, settings


def create(user, title, description, subtitle, language, author, category,
           explicit, image_id):
    show = models.Show(user, title, description, subtitle, language, author,
                       category, explicit, image_id)
    models.db.session.add(show)
    models.db.session.commit()
    return show


def update(user, show_id, title, description, subtitle, language, author,
           category, explicit, image_id):
    show = models.Show.query \
                      .filter_by(owner_user_id=user.id, id=show_id) \
                      .first()
    assert show, 'specified show does not exist'

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
    show = models.Show.query.\
        filter_by(owner_user_id=user.id, id=show_id).first()
    if show:
        return show
    else:
        raise AssertionError(
            'No such show. (user,show):({0},{1})'.format(user.id, show_id))


def get_show_url(show):
    # TODO
    return urllib.parse.urljoin(
        settings.HOST, 'user/{}/show/{}'.format(show.owner_user_id, show.id))


def get_show_unique_id(show):
    # TODO
    return '{}-{}'.format(show.owner_user_id, show.id)
