import datetime
import enum
import uuid
from flask_sqlalchemy import SQLAlchemy
from highland import app

db = SQLAlchemy(app)


class Show(db.Model):
    '''
    last_build_datetime: when the last public change under the show was made
    update_datetime: when the last change to the show entity was made
    '''
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                              primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    subtitle = db.Column(db.String(200))
    language = db.Column(db.String(10))
    author = db.Column(db.String(100))
    category = db.Column(db.String(50))
    explicit = db.Column(db.Boolean())
    image_id = db.Column(db.Integer)
    alias = db.Column(db.String(100), unique=True)
    last_build_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))
    update_datetime = db.Column(
        db.DateTime(timezone=True),
        onupdate=lambda x: datetime.datetime.now(datetime.timezone.utc))
    create_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))

    def __init__(self, user, title, description, subtitle, language, author,
                 category, explicit, image_id, alias):
        self.owner_user_id = user.id
        self.title = title
        self.description = description
        self.subtitle = subtitle
        self.language = language
        self.author = author
        self.category = category
        self.explicit = explicit
        self.image_id = image_id
        self.alias = alias

    def __iter__(self):
        for key in ['owner_user_id', 'id', 'title', 'description', 'subtitle',
                    'language', 'author', 'category', 'explicit', 'image_id',
                    'alias']:
            yield(key, getattr(self, key))
        yield('last_build_datetime', str(self.last_build_datetime))
        yield('update_datetime', str(self.update_datetime))
        yield('create_datetime', str(self.create_datetime))


class Episode(db.Model):
    class DraftStatus(enum.Enum):
        draft = 'draft'
        scheduled = 'scheduled'
        published = 'published'

    owner_user_id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    subtitle = db.Column(db.String(200))
    description = db.Column(db.Text())
    audio_id = db.Column(db.Integer)
    image_id = db.Column(db.Integer)
    draft_status = db.Column(db.Enum(DraftStatus.draft.name,
                                     DraftStatus.scheduled.name,
                                     DraftStatus.published.name,
                                     name='draft_status'))
    scheduled_datetime = db.Column(db.DateTime(timezone=True))
    explicit = db.Column(db.Boolean())
    guid = db.Column(db.String(32),
                     default=lambda x: uuid.uuid4().hex)
    alias = db.Column(db.String(100))
    update_datetime = db.Column(
        db.DateTime(timezone=True),
        onupdate=lambda x: datetime.datetime.now(datetime.timezone.utc))
    create_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['owner_user_id', 'show_id'],
            ['show.owner_user_id', 'show.id'],
        ),
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

    def __iter__(self):
        for key in ['owner_user_id', 'show_id', 'id', 'title', 'subtitle',
                    'description', 'audio_id', 'explicit', 'guid', 'image_id',
                    'alias']:
            yield(key, getattr(self, key))
        yield('draft_status', self.draft_status.name)
        yield('scheduled_datetime', str(self.scheduled_datetime))
        yield('update_datetime', str(self.update_datetime))
        yield('create_datetime', str(self.create_datetime))


class Audio(db.Model):
    '''
    duration: in seconds
    length: in bytes
    '''
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    duration = db.Column(db.Integer())
    length = db.Column(db.Integer())
    type = db.Column(db.String(30))
    guid = db.Column(db.String(32))
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

    def __iter__(self):
        for key in ['owner_user_id', 'id', 'filename', 'duration', 'length',
                    'type', 'guid']:
            yield(key, getattr(self, key))
        yield('create_datetime', str(self.create_datetime))


class Image(db.Model):
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                              primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    guid = db.Column(db.String(32))
    type = db.Column(db.String(10))
    create_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))

    def __init__(self, user, filename, guid, type):
        self.owner_user_id = user.id
        self.filename = filename
        self.guid = guid
        self.type = type

    def __iter__(self):
        for key in ['owner_user_id', 'id', 'filename', 'guid', 'type']:
            yield(key, getattr(self, key))
        yield('create_datetime', str(self.create_datetime))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    name = db.Column(db.String(100))
    update_datetime = db.Column(
        db.DateTime(timezone=True),
        onupdate=lambda x: datetime.datetime.now(datetime.timezone.utc))
    create_datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda x: datetime.datetime.now(datetime.timezone.utc))

    def __init__(self, username, email, password, name):
        self.username = username
        self.email = email
        self.password = password
        self.name = name

    def __iter__(self):
        for key in ['id', 'username', 'email', 'name']:
            yield(key, getattr(self, key))
        yield('update_datetime', str(self.update_datetime))
        yield('create_datetime', str(self.create_datetime))
