from highland import app, media_storage
from highland.common import verify_ownership
from highland.models import db, User


def delete(user_id, media_ids, model_class, get_key, bucket):
    """Deletes media objects both from database and file storage

    get_key: function of (user, media)
    that returns the string to be used as the key in the storage
    """
    targets = db.session. \
        query(model_class, User). \
        join(User). \
        filter(model_class.id.in_(media_ids)). \
        order_by(model_class.owner_user_id). \
        all()

    # execute the deletion only when ownership is correct for all
    for media, user in targets:
        verify_ownership(user_id, media)

    for media, user in targets:
        try:
            media_storage.delete(get_key(user, media), bucket)
        except:
            app.logger.error(
                'Failed to delete media:({},{})'.format(
                    user.id, media.id), exc_info=1)
        else:
            db.session.delete(media)
    db.session.commit()
    return True
