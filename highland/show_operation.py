from highland import models


def create(user, title, description):
    show = models.Show(user, title, description)
    models.db.session.add(show)
    models.db.session.commit()
    return show


def update(show, title, description):
    show.title = title
    show.description = description
    models.db.session.commit()
    return show
