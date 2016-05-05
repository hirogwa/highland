import datetime
import enum
from flask_sqlalchemy import SQLAlchemy
from highland import app

db = SQLAlchemy(app)


class Show(db.Model):
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                              primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    update_datetime = db.Column(db.DateTime(),
                                onupdate=datetime.datetime.utcnow)
    create_datetime = db.Column(db.DateTime(),
                                default=datetime.datetime.utcnow)

    def __init__(self, user, title, description):
        self.owner_user_id = user.id
        self.title = title
        self.description = description

    def __iter__(self):
        for key in ['owner_user_id', 'id', 'title', 'description']:
            yield(key, getattr(self, key))
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
    description = db.Column(db.Text())
    audio_id = db.Column(db.Integer)
    draft_status = db.Column(db.Enum(DraftStatus.draft.name,
                                     DraftStatus.scheduled.name,
                                     DraftStatus.published.name,
                                     name='draft_status'))
    scheduled_datetime = db.Column(db.DateTime())
    update_datetime = db.Column(db.DateTime(),
                                onupdate=datetime.datetime.utcnow)
    create_datetime = db.Column(db.DateTime(),
                                default=datetime.datetime.utcnow)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['owner_user_id', 'show_id'],
            ['show.owner_user_id', 'show.id'],
        ),
    )

    def __init__(self, show, title, description, audio_id, draft_status,
                 scheduled_datetime):
        self.owner_user_id = show.owner_user_id
        self.show_id = show.id
        self.title = title
        self.description = description
        self.audio_id = audio_id
        self.draft_status = draft_status
        self.scheduled_datetime = scheduled_datetime

    def __iter__(self):
        for key in ['owner_user_id', 'show_id', 'id', 'title', 'description',
                    'audio_id']:
            yield(key, getattr(self, key))
        yield('draft_status', self.draft_status.name)
        yield('scheduled_datetime', str(self.scheduled_datetime))
        yield('update_datetime', str(self.update_datetime))
        yield('create_datetime', str(self.create_datetime))


class Audio(db.Model):
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    create_datetime = db.Column(db.DateTime(),
                                default=datetime.datetime.utcnow)

    def __init__(self, user, filename):
        self.owner_user_id = user.id
        self.filename = filename

    def __iter__(self):
        for key in ['owner_user_id', 'id', 'filename']:
            yield(key, getattr(self, key))
        yield('create_datetime', str(self.create_datetime))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    update_datetime = db.Column(db.DateTime(),
                                onupdate=datetime.datetime.utcnow)
    create_datetime = db.Column(db.DateTime(),
                                default=datetime.datetime.utcnow)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __iter__(self):
        for key in ['id', 'username', 'email']:
            yield(key, getattr(self, key))
        yield('update_datetime', str(self.update_datetime))
        yield('create_datetime', str(self.create_datetime))
