from highland import models


def create(user, title, description):
    show = models.Show(user, title, description)
    models.db.session.add(show)
    models.db.session.commit()
    return show
