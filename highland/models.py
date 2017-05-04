import datetime
import enum
import uuid
from flask_sqlalchemy import SQLAlchemy
from highland import app, aws_resources


class ModelMappingMixin():
    """Iterable to present model as a mapping"""

    def __iter__(self):
        for key in (x.name for x in self.__table__.columns):
            yield key, getattr(self, key)


db = SQLAlchemy(app)


class Show(ModelMappingMixin, db.Model):
    """last_build_datetime: when the last public change under the show was made
    update_datetime: when the last change to the show entity was made
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    subtitle = db.Column(db.String(200))
    language = db.Column(db.String(10))
    author = db.Column(db.String(100))
    category = db.Column(db.String(50))
    explicit = db.Column(db.Boolean())
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    alias = db.Column(db.String(100), unique=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    last_build_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))
    update_datetime = db.Column(
        db.DateTime(timezone=True),
        onupdate=lambda x: datetime.datetime.now(datetime.timezone.utc))
    create_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))

    def __init__(self, user_id, title, description, subtitle, language, author,
                 category, explicit, image_id, alias):
        self.owner_user_id = user_id
        self.title = title
        self.description = description
        self.subtitle = subtitle
        self.language = language
        self.author = author
        self.category = category
        self.explicit = explicit
        self.image_id = image_id
        self.alias = alias


class Episode(ModelMappingMixin, db.Model):
    class DraftStatus(enum.Enum):
        draft = 'draft'
        scheduled = 'scheduled'
        published = 'published'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    subtitle = db.Column(db.String(200))
    description = db.Column(db.Text())
    audio_id = db.Column(db.Integer, db.ForeignKey('audio.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    draft_status = db.Column(db.Enum(DraftStatus.draft.name,
                                     DraftStatus.scheduled.name,
                                     DraftStatus.published.name,
                                     name='draft_status'))
    scheduled_datetime = db.Column(db.DateTime(timezone=True))
    published_datetime = db.Column(db.DateTime(timezone=True))
    explicit = db.Column(db.Boolean())
    guid = db.Column(db.String(32),
                     default=lambda x: uuid.uuid4().hex)
    alias = db.Column(db.String(100))
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), index=True)
    update_datetime = db.Column(
        db.DateTime(timezone=True),
        onupdate=lambda x: datetime.datetime.now(datetime.timezone.utc))
    create_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('show_id', 'alias'),
    )

    def __init__(self, show, title, subtitle, description, audio_id,
                 draft_status, scheduled_datetime, explicit, image_id, alias):
        self.owner_user_id = show.owner_user_id
        self.show_id = show.id
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.audio_id = audio_id
        self.draft_status = draft_status
        self.scheduled_datetime = scheduled_datetime
        self.explicit = explicit
        self.image_id = image_id
        self.alias = alias


class Audio(ModelMappingMixin, db.Model):
    """duration: in seconds
    length: in bytes
    """
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    duration = db.Column(db.Integer())
    length = db.Column(db.Integer())
    type = db.Column(db.String(30))
    guid = db.Column(db.String(32))
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    create_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))

    def __init__(self, user, filename, duration, length, type, guid):
        self.owner_user_id = user.id
        self.filename = filename
        self.duration = duration
        self.length = length
        self.type = type
        self.guid = guid


class Image(ModelMappingMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    guid = db.Column(db.String(32))
    type = db.Column(db.String(10))
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    create_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))

    def __init__(self, user, filename, guid, type):
        self.owner_user_id = user.id
        self.filename = filename
        self.guid = guid
        self.type = type


class User(ModelMappingMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(100))
    identity_id = db.Column(db.String(60))
    update_datetime = db.Column(
        db.DateTime(timezone=True),
        onupdate=lambda x: datetime.datetime.now(datetime.timezone.utc))
    create_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))

    def __init__(self, username, name, identity_id):
        self.username = username
        self.name = name
        self.identity_id = identity_id

    def __getattr__(self, name):
        if name == 'email':
            app.logger.info('Calling cognito_idp.admin_get_user for email')
            resp = aws_resources.cognito_idp.admin_get_user(
                UserPoolId=app.config.get('COGNITO_USER_POOL_ID'),
                Username=self.username
            )
            a = resp.get('UserAttributes')
            email = [x.get('Value') for x in a if x.get('Name') == 'email'][0]
            self.email = email
            return email
        raise AttributeError('unexpected attribute:{}'.format(name))
