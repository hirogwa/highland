import datetime
import unittest
from unittest.mock import MagicMock
from highland import show_operation, episode_operation, models, audio_operation


class TestEpisodeOperation(unittest.TestCase):
    @unittest.mock.patch.object(episode_operation, 'valid_or_assert')
    @unittest.mock.patch('highland.models.Episode')
    @unittest.mock.patch.object(audio_operation, 'get_audio_or_assert')
    @unittest.mock.patch.object(show_operation, 'get_show_or_assert')
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    def test_create(self, mocked_add, mocked_commit, mocked_get_show,
                    mocked_get_audio, mocked_episode_class, mocked_valid):
        mocked_user = MagicMock()
        mocked_show = MagicMock()
        mocked_show.id = 2
        mocked_audio = MagicMock()
        mocked_audio.id = 3
        status_published = models.Episode.DraftStatus.published

        title = 'my episode'
        description = 'my episode description'
        subtitle = 'my episode subtitle'
        explicit = True

        mocked_get_show.return_value = mocked_show
        mocked_get_audio.return_value = mocked_audio
        mocked_episode = MagicMock()
        mocked_episode_class.return_value = mocked_episode
        mocked_episode_class.DraftStatus.return_value = status_published
        mocked_valid.return_value = mocked_episode

        result = episode_operation.create(
            mocked_user, mocked_show.id, status_published.name, None,
            title, subtitle, description, mocked_audio.id, explicit)

        self.assertEqual(mocked_episode, result)
        mocked_episode_class.DraftStatus.assert_called_with(
            status_published.name)
        mocked_get_show.assert_called_with(mocked_user, mocked_show.id)
        mocked_episode_class.assert_called_with(
            mocked_show, title, subtitle, description, mocked_audio.id,
            status_published, None, explicit)
        mocked_valid.assert_called_with(mocked_user, mocked_episode)
        mocked_add.assert_called_with(mocked_episode)
        mocked_commit.assert_called_with()

    @unittest.mock.patch.object(audio_operation, 'get_audio_or_assert')
    def test_valid_or_assert_valid_published(self, mocked_get_audio):
        mocked_user = MagicMock()
        mocked_show = MagicMock()
        mocked_audio = MagicMock()
        mocked_audio.id = 3

        mocked_get_audio.return_value = mocked_audio

        episode = models.Episode(
            mocked_show, 'my episode', 'my subtitle', 'my episode desc',
            mocked_audio.id, models.Episode.DraftStatus.published, None, False)

        result = episode_operation.valid_or_assert(mocked_user, episode)

        self.assertEqual(episode, result)
        mocked_get_audio.assert_called_with(mocked_user, episode.audio_id)

    @unittest.mock.patch.object(audio_operation, 'get_audio_or_assert')
    def test_valid_or_assert_incomplete_draft(self, mocked_get_audio):
        mocked_user = MagicMock()
        mocked_show = MagicMock()

        episode = models.Episode(
            mocked_show, '', '', '', -1, models.Episode.DraftStatus.draft,
            None, False)

        result = episode_operation.valid_or_assert(mocked_user, episode)

        self.assertEqual(episode, result)
        mocked_get_audio.assert_not_called()

    def test_valid_or_assert_scheduled_with_no_time(self):
        mocked_user = MagicMock()
        mocked_show = MagicMock()
        episode = models.Episode(
            mocked_show, '', '', '', -1, models.Episode.DraftStatus.scheduled,
            None, False)

        with self.assertRaises(AssertionError):
            episode_operation.valid_or_assert(mocked_user, episode)

    @unittest.mock.patch.object(episode_operation, 'valid_or_assert')
    @unittest.mock.patch.object(episode_operation, 'get_episode_or_assert')
    @unittest.mock.patch.object(show_operation, 'get_show_or_assert')
    @unittest.mock.patch.object(models.db.session, 'commit')
    def test_update(self, mocked_commit,
                    mocked_get_show, mocked_get_episode, mocked_valid):
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
        mocked_episode.draft_status = models.Episode.DraftStatus.draft

        title = 'new title'
        subtitle = 'new sub title'
        description = 'new desc'
        explicit = True
        draft_status_new = models.Episode.DraftStatus.scheduled
        scheduled_datetime_new = datetime.datetime.utcnow()
        mocked_audio_new = MagicMock()
        mocked_audio_new.id = 11

        mocked_get_episode.return_value = mocked_episode

        result = episode_operation.update(
            mocked_user, mocked_show.id, mocked_episode.id,
            draft_status_new.name, scheduled_datetime_new, title, subtitle,
            description, mocked_audio_new.id, explicit)

        mocked_get_show.assert_called_with(mocked_user, mocked_show.id)
        mocked_get_episode.assert_called_with(
            mocked_user, mocked_show.id, mocked_episode.id)
        mocked_valid.assert_called_with(mocked_user, mocked_episode)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_show.owner_user_id,
                         mocked_episode.owner_user_id)
        self.assertEqual(mocked_show.id, mocked_episode.show_id)
        self.assertEqual(title, mocked_episode.title)
        self.assertEqual(subtitle, mocked_episode.subtitle)
        self.assertEqual(description, mocked_episode.description)
        self.assertEqual(mocked_audio_new.id, mocked_episode.audio_id)
        self.assertEqual(draft_status_new, mocked_episode.draft_status)
        self.assertEqual(scheduled_datetime_new,
                         mocked_episode.scheduled_datetime)
        self.assertEqual(explicit, mocked_episode.explicit)
        self.assertEqual(result, mocked_episode)

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'delete')
    def test_delete(self, mocked_delete, mocked_commit):
        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = 2

        mocked_audio = MagicMock()
        mocked_audio.id = 3

        episode = models.Episode(
            mocked_show, 'title', 'subtitle', 'desc', mocked_audio.id,
            models.Episode.DraftStatus.published, None, False)

        result = episode_operation.delete(episode)

        mocked_delete.assert_called_with(episode)
        mocked_commit.assert_called_with()
        self.assertTrue(result)

    @unittest.mock.patch.object(show_operation, 'get_show_or_assert')
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
            mocked_show, 'title one', 'sub one', 'desc one', mocked_audio.id,
            models.Episode.DraftStatus.published, None, False)
        ep_two = models.Episode(
            mocked_show, 'title two', 'sub two', 'desc two', mocked_audio.id,
            models.Episode.DraftStatus.draft, None, False)
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
