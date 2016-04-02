import unittest
from unittest.mock import MagicMock
from highland import episode_operation, models


class TestEpisodeOperation(unittest.TestCase):
    @unittest.mock.patch('highland.models.Episode')
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    def test_create(self, mocked_add, mocked_commit, mocked_episode_class):
        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = 2

        mocked_audio = MagicMock()
        mocked_audio.id = 3

        title = 'my episode'
        description = 'my episode description'

        mocked_episode = MagicMock()
        mocked_episode_class.return_value = mocked_episode

        result = episode_operation.create(
            mocked_show, title, description, mocked_audio)

        mocked_episode_class.assert_called_with(
            mocked_show, title, description, mocked_audio)
        mocked_add.assert_called_with(mocked_episode)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_episode, result)

    @unittest.mock.patch.object(models.db.session, 'commit')
    def test_update(self, mocked_commit):
        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = 2

        mocked_audio_original = MagicMock()
        mocked_audio_original.id = 3

        episode = models.Episode(mocked_show, 'original title',
                                 'original desc', mocked_audio_original)

        title = 'new title'
        description = 'new desc'
        mocked_audio_new = MagicMock()
        mocked_audio_new.id = 11

        result = episode_operation.update(
            episode, title, description, mocked_audio_new)

        mocked_commit.assert_called_with()
        self.assertEqual(mocked_show.owner_user_id, episode.owner_user_id)
        self.assertEqual(mocked_show.id, episode.show_id)
        self.assertEqual(title, episode.title)
        self.assertEqual(description, episode.description)
        self.assertEqual(mocked_audio_new.id, episode.audio_id)
        self.assertEqual(result, episode)

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'delete')
    def test_delete(self, mocked_delete, mocked_commit):
        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = 2

        mocked_audio = MagicMock()
        mocked_audio.id = 3

        episode = models.Episode(mocked_show, 'title', 'desc', mocked_audio)

        result = episode_operation.delete(episode)

        mocked_delete.assert_called_with(episode)
        mocked_commit.assert_called_with()
        self.assertTrue(result)

    @unittest.mock.patch('highland.models.Episode.query')
    def test_load(self, mocked_query):
        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = 2

        mocked_audio = MagicMock()
        mocked_audio.id = 3

        ep_one = models.Episode(
            mocked_show, 'title one', 'desc one', mocked_audio)
        ep_two = models.Episode(
            mocked_show, 'title two', 'desc two', mocked_audio)
        ep_list = [ep_one, ep_two]

        mocked_query.all.return_value = ep_list

        result = episode_operation.load()

        mocked_query.all.assert_called_with()
        self.assertEqual(ep_list, result)
