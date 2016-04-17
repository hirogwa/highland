import unittest
from unittest.mock import MagicMock
from highland import models


class TestShow(unittest.TestCase):
    def test_iter(self):
        user = MagicMock()
        user.id = 2
        show = models.Show(user, 'my title', 'my description')
        show.id = 1

        show_d = dict(show)

        self.assertEqual(4, len(show_d))
        self.assertEqual(show.owner_user_id, show_d.get('owner_user_id'))
        self.assertEqual(show.id, show_d.get('id'))
        self.assertEqual(show.title, show_d.get('title'))
        self.assertEqual(show.description, show_d.get('description'))


class TestEpisode(unittest.TestCase):
    def test_iter(self):
        show = MagicMock()
        show.owner_user_id = 1
        show.id = 2
        audio = MagicMock()
        audio.id = 3
        episode = models.Episode(show, 'my title', 'my description', audio)
        episode.id = 4

        episode_d = dict(episode)

        self.assertEqual(6, len(episode_d))
        self.assertEqual(episode.owner_user_id, episode_d.get('owner_user_id'))
        self.assertEqual(episode.show_id, episode_d.get('show_id'))
        self.assertEqual(episode.id, episode_d.get('id'))
        self.assertEqual(episode.title, episode_d.get('title'))
        self.assertEqual(episode.description, episode_d.get('description'))
        self.assertEqual(episode.audio_id, episode_d.get('audio_id'))


class TestAudio(unittest.TestCase):
    def test_iter(self):
        user = MagicMock()
        user.id = 1
        audio = models.Audio(user, 'my file name')
        audio.id = 2

        audio_d = dict(audio)

        self.assertEqual(3, len(audio_d))
        self.assertEqual(audio.owner_user_id, audio_d.get('owner_user_id'))
        self.assertEqual(audio.id, audio_d.get('id'))
        self.assertEqual(audio.filename, audio_d.get('filename'))
