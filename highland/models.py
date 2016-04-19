from flask_sqlalchemy import SQLAlchemy
from highland import app

db = SQLAlchemy(app)


class Show(db.Model):
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                              primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())

    def __init__(self, user, title, description):
        self.owner_user_id = user.id
        self.title = title
        self.description = description

    def __iter__(self):
        for key in ['owner_user_id', 'id', 'title', 'description']:
            yield(key, getattr(self, key))


class Episode(db.Model):
    owner_user_id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    audio_id = db.Column(db.Integer)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['owner_user_id', 'show_id'],
            ['show.owner_user_id', 'show.id'],
        ),
    )

    def __init__(self, show, title, description, audio):
        self.owner_user_id = show.owner_user_id
        self.show_id = show.id
        self.title = title
        self.description = description
        self.audio_id = audio.id if audio else -1

    def __iter__(self):
        for key in ['owner_user_id', 'show_id', 'id', 'title', 'description',
                    'audio_id']:
            yield(key, getattr(self, key))


class Audio(db.Model):
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))

    def __init__(self, user, filename):
        self.owner_user_id = user.id
        self.filename = filename

    def __iter__(self):
        for key in ['owner_user_id', 'id', 'filename']:
            yield(key, getattr(self, key))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __iter__(self):
        for key in ['id', 'username', 'email']:
            yield(key, getattr(self, key))
