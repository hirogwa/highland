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
        episode = models.Episode(mocked_show, title, description, mocked_audio)
        mocked_episode_class.return_value = episode

        result = episode_operation.create(
            mocked_show, title, description, mocked_audio)

        mocked_add.assert_called_with(episode)
        mocked_commit.assert_called_with()
        self.assertEqual(episode, result)
