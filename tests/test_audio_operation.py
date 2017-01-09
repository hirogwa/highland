import unittest
from unittest.mock import patch, MagicMock
from highland import audio_operation, models, media_storage, settings, \
    exception


class TestAudioOperation(unittest.TestCase):
    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'add')
    @patch('highland.models.Audio')
    @patch('uuid.uuid4')
    def test_create(
            self, mocked_uuid4, mocked_audio_class, mocked_add, mocked_commit):
        mocked_user, mocked_audio, mocked_uuid = \
            MagicMock(), MagicMock(), MagicMock()
        mocked_uuid4.return_value = mocked_uuid
        mocked_audio_class.return_value = mocked_audio

        result = audio_operation.create(
            mocked_user, 'some.mp3', 120, 6400, 'audio/mpeg')

        self.assertEqual(1, mocked_add.call_count)
        mocked_commit.assert_called_with()
        mocked_audio_class.assert_called_with(
            mocked_user, 'some.mp3', 120, 6400, 'audio/mpeg', mocked_uuid.hex)
        self.assertEqual(mocked_audio, result)

    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'delete')
    @patch.object(media_storage, 'delete')
    @patch.object(audio_operation, 'get_audio_or_assert')
    def test_delete(self, mocked_get_audio, mocked_media_delete,
                    mocked_delete, mocked_commit):
        mocked_audio, mocked_user = MagicMock(), MagicMock()
        mocked_user.identity_id = 'identity_id'
        mocked_audio.guid = 'someguid'
        audio_ids = [2]
        mocked_get_audio.return_value = mocked_audio

        result = audio_operation.delete(mocked_user, audio_ids)

        mocked_get_audio.assert_called_with(mocked_user, audio_ids[0])
        mocked_media_delete.assert_called_with(
            'identity_id/someguid', settings.S3_BUCKET_AUDIO)
        mocked_delete.assert_called_with(mocked_audio)
        mocked_commit.assert_called_with()
        self.assertTrue(result)

    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'delete')
    @patch.object(media_storage, 'delete')
    @patch.object(audio_operation, 'get_audio_or_assert')
    def test_delete_file_error(self, mocked_get_audio, mocked_media_delete,
                               mocked_delete, mocked_commit):
        mocked_user = MagicMock()
        audio_ids = [2]
        mocked_media_delete.side_effect = ValueError()

        audio_operation.delete(mocked_user, audio_ids)

        mocked_delete.assert_not_called()
        mocked_commit.assert_called_with()

    @patch.object(audio_operation, 'get_audio_url')
    @patch('highland.models.Episode.query')
    @patch('highland.models.Audio.query')
    def test_load(
            self, mocked_query_audio, mocked_query_episode, mocked_get_url):
        mocked_user = MagicMock()
        mocked_user.id = 1

        mocked_filter_audio = MagicMock()
        mocked_audio_01, mocked_audio_02, mocked_audio_03 = \
            MagicMock(), MagicMock(), MagicMock()
        mocked_audio_01.id = 11    # used
        mocked_audio_02.id = 12    # used but whitelisted
        mocked_audio_03.id = 13    # not used
        mocked_audio_01.__iter__.return_value = iter({'id': 11})
        mocked_audio_02.__iter__.return_value = iter({'id': 12})
        mocked_audio_03.__iter__.return_value = iter({'id': 13})
        mocked_filter_audio.all.return_value = [
            mocked_audio_01, mocked_audio_02, mocked_audio_03]
        mocked_query_audio.filter_by.return_value = mocked_filter_audio

        mocked_filter_episode = MagicMock()
        mocked_episode_01, mocked_episode_02, mocked_episode_03 = \
            MagicMock(), MagicMock(), MagicMock()
        mocked_episode_01.audio_id = 11    # used
        mocked_episode_02.audio_id = 12    # used but whitelisted
        mocked_episode_03.audio_id = None  # not used
        mocked_episode_01.id = 21
        mocked_episode_02.id = 22
        mocked_episode_03.id = 23
        mocked_filter_episode.all.return_value = [
            mocked_episode_01, mocked_episode_02, mocked_episode_03]
        mocked_query_episode.filter_by.return_value = mocked_filter_episode

        result = audio_operation.load(mocked_user, True, 12)

        mocked_query_audio.filter_by.assert_called_with(
            owner_user_id=mocked_user.id)
        mocked_filter_audio.all.assert_called_with()
        mocked_query_episode.filter_by.assert_called_with(
            owner_user_id=mocked_user.id)
        mocked_filter_episode.all.assert_called_with()
        self.assertEqual(2, len(result))
        self.assertEqual([22, None], [x['episode_id'] for x in result])

    @patch.object(audio_operation, 'access_allowed_or_raise')
    @patch('highland.models.Audio.query')
    def test_get_audio_or_assert(self, mocked_query, mocked_access):
        mocked_user, mocked_audio = MagicMock(), MagicMock()
        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_audio
        mocked_query.filter_by.return_value = mocked_filter

        result = audio_operation.get_audio_or_assert(
            mocked_user, mocked_audio.id)

        mocked_query.filter_by.assert_called_with(
            owner_user_id=mocked_user.id, id=mocked_audio.id)
        mocked_filter.first.assert_called_with()
        mocked_access.assert_called_with(mocked_user.id, mocked_audio)
        self.assertEqual(result, mocked_audio)

    @patch.object(audio_operation, 'access_allowed_or_raise')
    @patch('highland.models.Audio.query')
    def test_get_audio_or_assert_not_found(self, mocked_query, mocked_access):
        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(exception.NoSuchEntityError):
            audio_operation.get_audio_or_assert(MagicMock(), 1)
        mocked_access.assert_not_called()

    @patch.object(audio_operation, 'access_allowed_or_raise')
    def test_get_audio_url(self, mocked_access):
        mocked_user, mocked_audio = MagicMock(), MagicMock()
        mocked_user.identity_id = 'identity_id'
        mocked_audio.guid = 'someguid'

        result = audio_operation.get_audio_url(mocked_user, mocked_audio)

        mocked_access.assert_called_with(mocked_user.id, mocked_audio)
        self.assertEqual(
            '{}/identity_id/someguid'.format(settings.HOST_AUDIO), result)

    def test_access_allowed_or_raise(self):
        mocked_audio = MagicMock()
        mocked_audio.owner_user_id = 1
        result = audio_operation.access_allowed_or_raise(1, mocked_audio)
        self.assertEqual(mocked_audio, result)

    def test_access_allowed_or_raise_raise(self):
        mocked_audio = MagicMock()
        mocked_audio.owner_user_id = 2
        with self.assertRaises(exception.AccessNotAllowedError):
            audio_operation.access_allowed_or_raise(1, mocked_audio)
