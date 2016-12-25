from datetime import datetime, timezone
import unittest
from unittest.mock import patch, MagicMock
from highland import show_operation, episode_operation, models, audio_operation,\
    image_operation, exception, common


class TestEpisodeOperation(unittest.TestCase):
    @patch.object(episode_operation, '_update_show_build_datetime')
    @patch.object(episode_operation, '_valid_or_assert')
    @patch.object(audio_operation, 'get_audio_or_assert')
    @patch.object(episode_operation, '_autofill_attributes')
    @patch.object(show_operation, 'get_show_or_assert')
    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'add')
    def test_create(
            self, mocked_add, mocked_commit, mocked_get_show,
            mocked_autofill, mocked_get_audio, mocked_valid, mocked_build):
        mocked_user = MagicMock()
        mocked_show = MagicMock()
        mocked_show.id = 2
        mocked_audio = MagicMock()
        mocked_audio.id = 3
        mocked_image = MagicMock()
        mocked_image.id = 4

        title = 'my episode'
        description = 'my episode description'
        subtitle = 'my episode subtitle'
        explicit = True
        alias = 'myAlias'
        draft_status = 'published'

        episode = models.Episode(
            mocked_show, title, subtitle, description, mocked_audio.id,
            draft_status, None, explicit, mocked_image.id, alias)

        mocked_get_show.return_value = mocked_show
        mocked_get_audio.return_value = mocked_audio

        result = episode_operation.create(
            mocked_user, mocked_show.id, draft_status, alias,
            mocked_audio.id, mocked_image.id, None, title, subtitle,
            description, explicit)

        self.assertEqual(dict(episode), dict(result))
        mocked_get_show.assert_called_with(mocked_user, mocked_show.id)
        self.assertTrue(mocked_autofill.called)
        self.assertTrue(mocked_valid.called)
        self.assertTrue(mocked_add.called)
        mocked_commit.assert_called_with()
        self.assertTrue(mocked_build.called)

    @patch.object(episode_operation, '_update_show_build_datetime')
    @patch.object(models.db.session, 'commit')
    @patch.object(episode_operation, '_valid_or_assert')
    @patch.object(episode_operation, '_autofill_attributes')
    @patch.object(episode_operation, 'get_episode_or_assert')
    def test_update(self, mocked_get_episode, mocked_autofill,
                    mocked_valid, mocked_commit, mocked_build):
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

        title = 'new title'
        subtitle = 'new sub title'
        description = 'new desc'
        explicit = True
        scheduled_datetime_new = datetime.utcnow()
        mocked_audio_new = MagicMock()
        mocked_audio_new.id = 11
        mocked_image_new = MagicMock()
        mocked_image_new.id = 12
        alias = 'new alias'
        status_new = 'published'

        mocked_get_episode.return_value = mocked_episode

        result = episode_operation.update(
            mocked_user, mocked_episode.id, draft_status=status_new,
            alias=alias, audio_id=mocked_audio_new.id,
            image_id=mocked_image_new.id,
            scheduled_datetime=scheduled_datetime_new, title=title,
            subtitle=subtitle, description=description, explicit=explicit)

        mocked_get_episode.assert_called_with(mocked_user, mocked_episode.id)
        mocked_autofill.assert_called_with(mocked_user, mocked_episode)
        mocked_valid.assert_called_with(mocked_user, mocked_episode)
        mocked_commit.assert_called_with()
        mocked_build.assert_called_with(mocked_user, mocked_episode)
        self.assertEqual(mocked_show.owner_user_id,
                         mocked_episode.owner_user_id)
        self.assertEqual(mocked_show.id, mocked_episode.show_id)
        self.assertEqual(title, mocked_episode.title)
        self.assertEqual(subtitle, mocked_episode.subtitle)
        self.assertEqual(description, mocked_episode.description)
        self.assertEqual(mocked_audio_new.id, mocked_episode.audio_id)
        self.assertEqual(status_new, mocked_episode.draft_status)
        self.assertEqual(scheduled_datetime_new,
                         mocked_episode.scheduled_datetime)
        self.assertEqual(explicit, mocked_episode.explicit)
        self.assertEqual(alias, mocked_episode.alias)
        self.assertEqual(result, mocked_episode)

    @patch.object(episode_operation,
                  '_update_show_build_datetime')
    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'delete')
    @patch.object(episode_operation, 'get_episode_or_assert')
    def test_delete(self, mocked_get_episode, mocked_delete, mocked_commit,
                    mocked_build):
        mocked_user = MagicMock()
        mocked_episode = MagicMock()
        episode_ids = [2]

        mocked_get_episode.return_value = mocked_episode

        result = episode_operation.delete(mocked_user, episode_ids)

        mocked_get_episode.assert_called_with(mocked_user, episode_ids[0])
        mocked_delete.assert_called_with(mocked_episode)
        mocked_commit.assert_called_with()
        mocked_build.assert_called_with(mocked_user, mocked_episode)
        self.assertTrue(result)

    @patch.object(show_operation, 'get_show_or_assert')
    @patch('highland.models.Episode.query')
    def test_load(self, mocked_query, mocked_get_show):
        mocked_user = MagicMock()
        mocked_user.id = 1
        mocked_show = MagicMock()
        mocked_show.owner_user_id = mocked_user.id
        mocked_show.id = 2
        mocked_get_show.return_value = mocked_show

        ep_list = [MagicMock(), MagicMock()]

        mocked_order = MagicMock()
        mocked_order.all.return_value = ep_list
        mocked_filter = MagicMock()
        mocked_filter.order_by.return_value = mocked_order
        mocked_query.filter_by.return_value = mocked_filter

        result = episode_operation.load(mocked_user, mocked_show.id)

        mocked_query.filter_by.assert_called_with(
            owner_user_id=mocked_show.owner_user_id,
            show_id=mocked_show.id)
        self.assertTrue(mocked_filter.order_by.called)
        mocked_order.all.assert_called_with()
        self.assertEqual(ep_list, result)

    @patch('highland.models.db.session.query')
    @patch.object(show_operation, 'get_show_or_assert')
    def test_load_with_audio(self, mocked_get_show, mocked_query):
        mocked_user, mocked_show = MagicMock(), MagicMock()
        mocked_get_show.return_value = mocked_show

        episode_operation.load_with_audio(mocked_user, mocked_show.id)

        mocked_get_show.assert_called_with(mocked_user, mocked_show.id)
        self.assertTrue(mocked_query.called)

    @patch('highland.models.Episode.query')
    @patch.object(show_operation, 'get_show_or_assert')
    def test_load_public(self, mocked_get_show, mocked_query):
        mocked_user, mocked_show = MagicMock(), MagicMock()
        mocked_get_show.return_value = mocked_show

        ep_list = MagicMock()
        mocked_order = MagicMock()
        mocked_order.all.return_value = ep_list
        mocked_filter = MagicMock()
        mocked_filter.order_by.return_value = mocked_order
        mocked_query.filter_by.return_value = mocked_filter

        result = episode_operation.load_public(mocked_user, mocked_show.id)

        self.assertEqual(ep_list, result)
        mocked_get_show.assert_called_with(mocked_user, mocked_show.id)
        mocked_query.filter_by.assert_called_with(
            owner_user_id=mocked_user.id, show_id=mocked_show.id,
            draft_status=models.Episode.DraftStatus.published.name)
        self.assertTrue(mocked_filter.order_by.called)
        mocked_order.all.assert_called_with()

    @patch('highland.models.Episode.query')
    def test_load_publish_target(self, mocked_query):
        episode_operation.load_publish_target()
        mocked_query.filter_by.assert_called_with(
            draft_status=models.Episode.DraftStatus.scheduled.name)

    @patch.object(models.db.session, 'commit')
    def test_publish(self, mocked_commit):
        mocked_episode = MagicMock()

        result = episode_operation.publish(mocked_episode)

        self.assertEqual(result, mocked_episode)
        self.assertEqual(models.Episode.DraftStatus.published.name,
                         mocked_episode.draft_status)
        mocked_commit.assert_called_with()

    @patch.object(models.db.session, 'commit')
    def test_publish_published(self, mocked_commit):
        mocked_episode = MagicMock()
        mocked_episode.draft_status = models.Episode.DraftStatus.published.name
        mocked_date = MagicMock()
        mocked_episode.published_datetime = mocked_date

        result = episode_operation.publish(mocked_episode)

        self.assertEqual(mocked_episode, result)
        self.assertEqual(models.Episode.DraftStatus.published.name,
                         mocked_episode.draft_status)
        self.assertEqual(mocked_date, mocked_episode.published_datetime)
        mocked_commit.assert_not_called()

    @patch.object(episode_operation, 'access_allowed_or_raise')
    @patch('highland.models.Episode.query')
    def test_get_episode_or_assert(self, mocked_query, mocked_access):
        mocked_user = MagicMock()
        mocked_user.id = 1
        mocked_episode = MagicMock()
        mocked_episode.id = 3

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_episode
        mocked_query.filter_by.return_value = mocked_filter

        result = episode_operation.get_episode_or_assert(
            mocked_user, mocked_episode.id)

        self.assertEqual(result, mocked_episode)
        mocked_query.filter_by.assert_called_with(
            owner_user_id=mocked_user.id, id=mocked_episode.id)
        mocked_filter.first.assert_called_with()
        mocked_access.assert_called_with(mocked_user.id, mocked_episode)

    @patch('highland.models.Episode.query')
    def test_get_episode_or_assert_not_found(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        episode_id = 3

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(exception.NoSuchEntityError):
            episode_operation.get_episode_or_assert(mocked_user, episode_id)

    @patch.object(show_operation, 'access_allowed_or_raise')
    @patch.object(episode_operation, 'access_allowed_or_raise')
    def test_get_episode_url(self, mocked_access, mocked_show_access):
        mocked_user, mocked_episode, mocked_show = \
            MagicMock(), MagicMock(), MagicMock()

        episode_operation.get_episode_url(
            mocked_user, mocked_episode, mocked_show)

        mocked_access.assert_called_with(mocked_user.id, mocked_episode)
        mocked_show_access.assert_called_with(mocked_user.id, mocked_show)

    @patch.object(show_operation, 'get_show_or_assert')
    @patch.object(episode_operation, 'access_allowed_or_raise')
    def test_get_episode_url_no_show_passed(
            self, mocked_access, mocked_get_show):
        mocked_user, mocked_episode = MagicMock(), MagicMock()

        episode_operation.get_episode_url(mocked_user, mocked_episode)

        mocked_access.assert_called_with(mocked_user.id, mocked_episode)
        mocked_get_show.assert_called_with(mocked_user, mocked_episode.show_id)

    def test_get_preview_episode(self):
        episode_operation.get_preview_episode(
            MagicMock(), MagicMock(), '', '', '', 1, 2)

    @patch('highland.models.db.session.query')
    def test_get_default_alias(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        show_id = 2
        mocked_filter = MagicMock()
        mocked_filter.all.return_value = ['1', '3']
        mocked_query_result = MagicMock()
        mocked_query_result.filter.return_value = mocked_filter
        mocked_query.return_value = mocked_query_result

        result = episode_operation.get_default_alias(mocked_user, show_id)

        self.assertEqual('4', result)
        mocked_query.assert_called_with(models.Episode.alias)
        self.assertEqual(1, mocked_query_result.filter.call_count)
        mocked_filter.all.assert_called_with()

    def test_access_allowed_or_raise(self):
        mocked_episode = MagicMock()
        mocked_episode.owner_user_id = 1

        result = episode_operation.access_allowed_or_raise(1, mocked_episode)

        self.assertEqual(mocked_episode, result)

    def test_access_allowed_or_raise_raise(self):
        mocked_episode = MagicMock()
        mocked_episode.owner_user_id = 1

        with self.assertRaises(exception.AccessNotAllowedError):
            episode_operation.access_allowed_or_raise(2, mocked_episode)

    @patch.object(common, 'require_true')
    @patch.object(image_operation, 'get_image_or_assert')
    @patch.object(audio_operation, 'get_audio_or_assert')
    @patch.object(common, 'is_valid_alias')
    def test_valid_or_assert_pass_all(
            self, mocked_valid_alias, mocked_get_audio, mocked_get_image,
            mocked_require_true):
        mocked_user, mocked_episode = MagicMock(), MagicMock()
        mocked_episode.audio_id = 1
        mocked_episode.image_id = 2
        mocked_episode.draft_status = models.Episode.DraftStatus.scheduled.name
        mocked_valid_alias.return_value = True

        result = episode_operation._valid_or_assert(
            mocked_user, mocked_episode)

        self.assertEqual(mocked_episode, result)
        mocked_get_audio.assert_called_with(
            mocked_user, mocked_episode.audio_id)
        mocked_get_image.assert_called_with(
            mocked_user, mocked_episode.image_id)
        self.assertEqual(4, mocked_require_true.call_count)

    @patch.object(common, 'is_valid_alias')
    def test_valid_or_assert_bad_alias(self, mocked_valid_alias):
        mocked_user, mocked_episode = MagicMock(), MagicMock()
        mocked_valid_alias.return_value = False
        with self.assertRaises(exception.InvalidValueError):
            episode_operation._valid_or_assert(mocked_user, mocked_episode)

    @patch.object(models.db.session, 'commit')
    @patch.object(show_operation, 'get_show_or_assert')
    def test_update_show_build_datetime(self, mocked_get_show, mocked_commit):
        mocked_user, mocked_episode, mocked_show = \
            MagicMock(), MagicMock(), MagicMock()
        mocked_episode.draft_status = models.Episode.DraftStatus.published.name
        mocked_get_show.return_value = mocked_show

        result = episode_operation._update_show_build_datetime(
            mocked_user, mocked_episode)

        mocked_get_show.assert_called_with(mocked_user, mocked_episode.show_id)
        self.assertTrue(
            datetime_almost_utcnow(mocked_show.last_build_datetime))
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_show, result)

    def test_update_show_build_datetime_not_published(self):
        mocked_user, mocked_episode = MagicMock(), MagicMock()

        result = episode_operation._update_show_build_datetime(
            mocked_user, mocked_episode)

        self.assertIsNone(result)

    @patch.object(episode_operation, 'get_default_alias')
    def test_autofill_attributes_draft(self, mocked_get_alias):
        mocked_user, mocked_episode, mocked_datetime = \
            MagicMock(), MagicMock(), MagicMock()
        mocked_episode.alias = None
        mocked_episode.draft_status = models.Episode.DraftStatus.draft.name
        mocked_get_alias.return_value = 'some_alias'
        mocked_episode.scheduled_datetime = mocked_datetime

        result = episode_operation._autofill_attributes(
            mocked_user, mocked_episode)

        self.assertEqual(mocked_episode, result)
        self.assertEqual('some_alias', mocked_episode.alias)
        self.assertIsNone(mocked_episode.published_datetime)
        self.assertIsNone(mocked_episode.scheduled_datetime)
        mocked_get_alias.assert_called_with(
            mocked_user, mocked_episode.show_id)

    @patch.object(episode_operation, 'get_default_alias')
    def test_autofill_attributes_scheduled(self, mocked_get_alias):
        mocked_user, mocked_episode, mocked_datetime = \
            MagicMock(), MagicMock(), MagicMock()
        mocked_episode.alias = 'some_alias'
        mocked_episode.draft_status = models.Episode.DraftStatus.scheduled.name
        mocked_episode.scheduled_datetime = mocked_datetime

        result = episode_operation._autofill_attributes(
            mocked_user, mocked_episode)

        self.assertEqual(mocked_episode, result)
        self.assertEqual('some_alias', mocked_episode.alias)
        self.assertIsNone(mocked_episode.published_datetime)
        self.assertEqual(mocked_datetime, mocked_episode.scheduled_datetime)
        mocked_get_alias.assert_not_called()

    @patch.object(episode_operation, 'get_default_alias')
    def test_autofill_attributes_published(self, mocked_get_alias):
        mocked_user, mocked_episode, mocked_datetime = \
            MagicMock(), MagicMock(), MagicMock()
        mocked_episode.alias = 'some_alias'
        mocked_episode.draft_status = models.Episode.DraftStatus.published.name
        mocked_episode.scheduled_datetime = mocked_datetime

        result = episode_operation._autofill_attributes(
            mocked_user, mocked_episode)

        self.assertEqual(mocked_episode, result)
        self.assertEqual('some_alias', mocked_episode.alias)
        self.assertTrue(datetime_almost_utcnow(
            mocked_episode.published_datetime))
        self.assertIsNone(mocked_episode.scheduled_datetime)
        mocked_get_alias.assert_not_called()


def datetime_almost_utcnow(x):
    return abs((x - datetime.now(timezone.utc)).total_seconds()) < 10
