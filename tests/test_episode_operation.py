import unittest
from unittest.mock import MagicMock
from highland import episode_operation, models


class TestEpisodeOperation(unittest.TestCase):
    @unittest.mock.patch.object(episode_operation, '_create_published')
    @unittest.mock.patch.object(episode_operation, 'get_show_or_assert')
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    def test_create_complete(self, mocked_add, mocked_commit, mocked_get_show,
                             mocked_create_published):
        mocked_user = MagicMock()
        mocked_user.id = 1
        mocked_show = MagicMock()
        mocked_show.owner_user_id = mocked_user.id
        mocked_show.id = 2
        mocked_audio = MagicMock()
        mocked_audio.id = 3

        title = 'my episode'
        description = 'my episode description'

        mocked_get_show.return_value = mocked_show
        mocked_episode = MagicMock()
        mocked_create_published.return_value = mocked_episode

        result = episode_operation.create(
            mocked_user, mocked_show.id, title, description, mocked_audio.id)

        mocked_get_show.assert_called_with(mocked_user, mocked_show.id)
        mocked_create_published.assert_called_with(
            mocked_user, mocked_show, title, description, mocked_audio.id)
        mocked_add.assert_called_with(mocked_episode)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_episode, result)

    @unittest.mock.patch.object(episode_operation, '_create_draft')
    @unittest.mock.patch.object(episode_operation, 'get_show_or_assert')
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    def test_create_incomplete(self, mocked_add, mocked_commit,
                               mocked_get_show, mocked_create_draft):
        mocked_user = MagicMock()
        mocked_user.id = 1
        mocked_show = MagicMock()
        mocked_show.owner_user_id = mocked_user.id
        mocked_show.id = 2

        mocked_get_show.return_value = mocked_show
        mocked_episode = MagicMock()
        mocked_create_draft.return_value = mocked_episode

        result = episode_operation.create(mocked_user, mocked_show.id)

        mocked_get_show.assert_called_with(mocked_user, mocked_show.id)
        mocked_create_draft.assert_called_with(
            mocked_user, mocked_show, '', '', -1)
        mocked_add.assert_called_with(mocked_episode)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_episode, result)

    @unittest.mock.patch.object(episode_operation, 'get_audio_or_assert')
    @unittest.mock.patch('highland.models.Episode')
    def test_create_published(self, mocked_episode_class, mocked_get_audio):
        mocked_user = MagicMock()
        mocked_show = MagicMock()
        mocked_audio = MagicMock()
        mocked_audio.id = 1
        mocked_get_audio.return_value = mocked_audio
        mocked_episode = MagicMock()
        mocked_episode_class.return_value = mocked_episode
        title = 'some title'
        description = 'some description'

        result = episode_operation._create_published(
            mocked_user, mocked_show, title, description, mocked_audio.id)

        self.assertEqual(mocked_episode, result)
        mocked_get_audio.assert_called_with(mocked_user, mocked_audio.id)
        mocked_episode_class.assert_called_with(
            mocked_show, title, description, mocked_audio.id,
            models.Episode.DraftStatus.ready)

    @unittest.mock.patch('highland.models.Episode')
    def test_create_draft(self, mocked_episode_class):
        mocked_user = MagicMock()
        mocked_show = MagicMock()
        mocked_episode = MagicMock()
        mocked_episode_class.return_value = mocked_episode

        result = episode_operation._create_draft(mocked_user, mocked_show)

        self.assertEqual(mocked_episode, result)
        mocked_episode_class.assert_called_with(
            mocked_show, '', '', -1, models.Episode.DraftStatus.draft)

    @unittest.mock.patch.object(episode_operation, 'get_audio_or_assert')
    @unittest.mock.patch.object(episode_operation, 'get_episode_or_assert')
    @unittest.mock.patch.object(episode_operation, 'get_show_or_assert')
    @unittest.mock.patch.object(models.db.session, 'commit')
    def test_update(self, mocked_commit,
                    mocked_get_show, mocked_get_episode, mocked_get_audio):
        mocked_user = MagicMock()
        mocked_user.id = 1

        mocked_show = MagicMock()
        mocked_show.owner_user_id = 2
        mocked_show.id = 3

        mocked_audio_original = MagicMock()
        mocked_audio_original.id = 4

        mocked_episode = MagicMock()
        mocked_episode.owner_user_id = mocked_show.owner_user_id
        mocked_episode.show_id = mocked_show.id
        mocked_episode.title = 'title original'
        mocked_episode.description = 'desc original'
        mocked_episode.audio_id = mocked_audio_original.id

        title = 'new title'
        description = 'new desc'
        mocked_audio_new = MagicMock()
        mocked_audio_new.id = 11

        mocked_get_episode.return_value = mocked_episode
        mocked_get_audio.return_value = mocked_audio_new

        result = episode_operation.update(
            mocked_user, mocked_show.id, mocked_episode.id, title,
            description, mocked_audio_new.id)

        mocked_get_show.assert_called_with(mocked_user, mocked_show.id)
        mocked_get_episode.assert_called_with(
            mocked_user, mocked_show.id, mocked_episode.id)
        mocked_get_audio.assert_called_with(mocked_user, mocked_audio_new.id)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_show.owner_user_id,
                         mocked_episode.owner_user_id)
        self.assertEqual(mocked_show.id, mocked_episode.show_id)
        self.assertEqual(title, mocked_episode.title)
        self.assertEqual(description, mocked_episode.description)
        self.assertEqual(mocked_audio_new.id, mocked_episode.audio_id)
        self.assertEqual(result, mocked_episode)

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'delete')
    def test_delete(self, mocked_delete, mocked_commit):
        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = 2

        mocked_audio = MagicMock()
        mocked_audio.id = 3

        episode = models.Episode(mocked_show, 'title', 'desc', mocked_audio,
                                 models.Episode.DraftStatus.ready)

        result = episode_operation.delete(episode)

        mocked_delete.assert_called_with(episode)
        mocked_commit.assert_called_with()
        self.assertTrue(result)

    @unittest.mock.patch.object(episode_operation, 'get_show_or_assert')
    @unittest.mock.patch('highland.models.Episode.query')
    def test_load(self, mocked_query, mocked_get_show):
        mocked_user = MagicMock()
        mocked_user.id = 1
        mocked_show = MagicMock()
        mocked_show.owner_user_id = mocked_user.id
        mocked_show.id = 2
        mocked_audio = MagicMock()
        mocked_audio.id = 3
        mocked_get_show.return_value = mocked_show

        ep_one = models.Episode(
            mocked_show, 'title one', 'desc one', mocked_audio,
            models.Episode.DraftStatus.ready)
        ep_two = models.Episode(
            mocked_show, 'title two', 'desc two', mocked_audio,
            models.Episode.DraftStatus.draft)
        ep_list = [ep_one, ep_two]

        mocked_filter = MagicMock()
        mocked_filter.all.return_value = ep_list
        mocked_query.filter_by.return_value = mocked_filter

        result = episode_operation.load(mocked_user, mocked_show.id)

        mocked_query.filter_by.assert_called_with(
            owner_user_id=mocked_show.owner_user_id,
            show_id=mocked_show.id)
        mocked_filter.all.assert_called_with()
        self.assertEqual(ep_list, result)

    @unittest.mock.patch('highland.models.Show.query')
    def test_get_show_or_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        mocked_show = MagicMock()
        mocked_show.owner_user_id = mocked_user.id
        mocked_show.id = 2

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_show
        mocked_query.filter_by.return_value = mocked_filter

        result = episode_operation.get_show_or_assert(
            mocked_user, mocked_show.id)

        mocked_query.filter_by.assert_called_with(owner_user_id=mocked_user.id,
                                                  id=mocked_show.id)
        mocked_filter.first.assert_called_with()
        self.assertEqual(result, mocked_show)

    @unittest.mock.patch('highland.models.Show.query')
    def test_get_show_or_assert_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        show_id = 2

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(AssertionError):
            episode_operation.get_show_or_assert(
                mocked_user, show_id)

    @unittest.mock.patch('highland.models.Audio.query')
    def test_get_audio_or_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        mocked_audio = MagicMock()
        mocked_audio.owner_user_id = mocked_user.id
        mocked_audio.id = 2

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_audio
        mocked_query.filter_by.return_value = mocked_filter

        result = episode_operation.get_audio_or_assert(
            mocked_user, mocked_audio.id)

        mocked_query.filter_by.assert_called_with(owner_user_id=mocked_user.id,
                                                  id=mocked_audio.id)
        mocked_filter.first.assert_called_with()
        self.assertEqual(result, mocked_audio)

    @unittest.mock.patch('highland.models.Audio.query')
    def test_get_audio_or_assert_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        audio_id = 2

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(AssertionError):
            episode_operation.get_audio_or_assert(
                mocked_user, audio_id)

    @unittest.mock.patch('highland.models.Episode.query')
    def test_get_episode_or_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        show_id = 2
        mocked_episode = MagicMock()
        mocked_episode.id = 3

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_episode
        mocked_query.filter_by.return_value = mocked_filter

        result = episode_operation.get_episode_or_assert(
            mocked_user, show_id, mocked_episode.id)

        mocked_query.filter_by.assert_called_with(owner_user_id=mocked_user.id,
                                                  show_id=show_id,
                                                  id=mocked_episode.id)
        mocked_filter.first.assert_called_with()
        self.assertEqual(result, mocked_episode)

    @unittest.mock.patch('highland.models.Episode.query')
    def test_get_episode_or_assert_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        show_id = 2
        episode_id = 3

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(AssertionError):
            episode_operation.get_episode_or_assert(
                mocked_user, show_id, episode_id)
