import datetime
import unittest
import uuid
from unittest.mock import MagicMock
from highland import models


class TestShow(unittest.TestCase):
    def test_iter(self):
        user = MagicMock()
        user.id = 2
        show = models.Show(user, 'my title', 'my description',
                           'this is my fun talk show on arts', 'en-US',
                           'Ultraman Ace, Ultraman Taro', 'Arts', False)
        show.id = 1

        show_d = dict(show)

        self.assertEqual(12, len(show_d))
        self.assertEqual(show.owner_user_id, show_d.get('owner_user_id'))
        self.assertEqual(show.id, show_d.get('id'))
        self.assertEqual(show.title, show_d.get('title'))
        self.assertEqual(show.description, show_d.get('description'))
        self.assertEqual(show.subtitle, show_d.get('subtitle'))
        self.assertEqual(show.language, show_d.get('language'))
        self.assertEqual(show.author, show_d.get('author'))
        self.assertEqual(show.category, show_d.get('category'))
        self.assertEqual(show.explicit, show_d.get('explicit'))
        self.assertIsNotNone(show_d.get('last_build_datetime'))
        self.assertIsNotNone(show_d.get('update_datetime'))
        self.assertIsNotNone(show_d.get('create_datetime'))


class TestEpisode(unittest.TestCase):
    def test_iter(self):
        show = MagicMock()
        show.owner_user_id = 1
        show.id = 2
        audio = MagicMock()
        audio.id = 3
        episode = models.Episode(
            show, 'my title', 'my subtitle', 'my description', audio.id,
            models.Episode.DraftStatus.scheduled,
            datetime.datetime.now(datetime.timezone.utc), False)
        episode.id = 4
        episode.guid = uuid.uuid4().hex
        episode.update_datetime = datetime.datetime.now(datetime.timezone.utc)
        episode.create_datetime = datetime.datetime.now(datetime.timezone.utc)

        episode_d = dict(episode)

        self.assertEqual(13, len(episode_d))
        self.assertEqual(episode.owner_user_id, episode_d.get('owner_user_id'))
        self.assertEqual(episode.show_id, episode_d.get('show_id'))
        self.assertEqual(episode.id, episode_d.get('id'))
        self.assertEqual(episode.title, episode_d.get('title'))
        self.assertEqual(episode.subtitle, episode_d.get('subtitle'))
        self.assertEqual(episode.description, episode_d.get('description'))
        self.assertEqual(episode.audio_id, episode_d.get('audio_id'))
        self.assertEqual(episode.draft_status.name,
                         episode_d.get('draft_status'))
        self.assertEqual(episode.explicit, episode_d.get('explicit'))
        self.assertEqual(episode.guid, episode_d.get('guid'))
        self.assertEqual(str(episode.update_datetime),
                         episode_d.get('update_datetime'))
        self.assertEqual(str(episode.create_datetime),
                         episode_d.get('create_datetime'))
        self.assertEqual(str(episode.scheduled_datetime),
                         episode_d.get('scheduled_datetime'))


class TestAudio(unittest.TestCase):
    def test_iter(self):
        user = MagicMock()
        user.id = 1
        audio = models.Audio(user, 'my file name', 1800, 5000000, 'audio/mpeg')
        audio.id = 2
        audio.create_datetime = datetime.datetime.now(datetime.timezone.utc)

        audio_d = dict(audio)

        self.assertEqual(7, len(audio_d))
        self.assertEqual(audio.owner_user_id, audio_d.get('owner_user_id'))
        self.assertEqual(audio.id, audio_d.get('id'))
        self.assertEqual(audio.filename, audio_d.get('filename'))
        self.assertEqual(audio.duration, audio_d.get('duration'))
        self.assertEqual(audio.length, audio_d.get('length'))
        self.assertEqual(audio.type, audio_d.get('type'))
        self.assertEqual(str(audio.create_datetime),
                         audio_d.get('create_datetime'))


class TestUser(unittest.TestCase):
    def test_iter(self):
        user = models.User('name', 'mail@example.com', 'strong password',
                           'Ultraman Taro')
        user_d = dict(user)

        self.assertEqual(6, len(user_d))
        self.assertEqual(user.id, user_d.get('id'))
        self.assertEqual(user.username, user_d.get('username'))
        self.assertEqual(user.email, user_d.get('email'))
        self.assertEqual(user.name, user_d.get('name'))
        self.assertIsNotNone(user_d.get('update_datetime'))
        self.assertIsNotNone(user_d.get('create_datetime'))
