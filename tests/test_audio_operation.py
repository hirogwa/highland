import uuid
import unittest
from unittest.mock import patch, MagicMock
from highland import audio_operation, models, media_storage, settings, \
    exception


class TestAudioOperation(unittest.TestCase):
    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'add')
    @patch.object(audio_operation, 'store_audio_data')
    def test_create(self, mocked_store, mocked_add, mocked_commit):
        mocked_user, mocked_audio_file = MagicMock(), MagicMock()
        guid = uuid.uuid4().hex
        duration = 1200
        length = 19000000
        type = 'audio/mpeg'
        mocked_store.return_value = guid, duration, length, type

        result = audio_operation.create(mocked_user, mocked_audio_file)

        mocked_store.assert_called_with(mocked_user, mocked_audio_file)
        self.assertEqual(1, mocked_add.call_count)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_user.id, result.owner_user_id)
        self.assertEqual(mocked_audio_file.filename, result.filename)
        self.assertEqual(duration, result.duration)
        self.assertEqual(length, result.length)
        self.assertEqual(type, result.type)
        self.assertEqual(guid, result.guid)

    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'delete')
    @patch.object(media_storage, 'delete')
    @patch.object(audio_operation, 'get_audio_or_assert')
    def test_delete(self, mocked_get_audio, mocked_media_delete,
                    mocked_delete, mocked_commit):
        mocked_audio, mocked_user = MagicMock(), MagicMock()
        audio_ids = [2]
        mocked_get_audio.return_value = mocked_audio

        result = audio_operation.delete(mocked_user, audio_ids)

        mocked_get_audio.assert_called_with(mocked_user, audio_ids[0])
        mocked_media_delete.assert_called_with(
            mocked_audio.guid, settings.S3_BUCKET_AUDIO, mocked_user.username)
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
        mocked_user.username = 'somename'
        mocked_audio.guid = 'someguid'

        result = audio_operation.get_audio_url(mocked_user, mocked_audio)

        mocked_access.assert_called_with(mocked_user.id, mocked_audio)
        self.assertEqual(
            '{}/somename/someguid'.format(settings.HOST_AUDIO), result)

    @patch('os.remove')
    @patch('os.stat')
    @patch('highland.audio_operation.MP3')
    @patch.object(media_storage, 'upload')
    @patch.object(uuid, 'uuid4')
    @patch('os.mkdir')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_store_audio_data(
            self, mocked_open, mocked_exists, mocked_mkdir, mocked_uuid4,
            mocked_upload, mocked_mp3, mocked_stat, mocked_remove):
        mocked_user, mocked_file = MagicMock(), MagicMock()
        mocked_user.username = 'username'
        mocked_exists.return_value = False
        mocked_uuid = MagicMock()
        mocked_uuid.hex = 'someguid'
        mocked_uuid4.return_value = mocked_uuid

        result = audio_operation.store_audio_data(mocked_user, mocked_file)

        mocked_exists.assert_called_with('username')
        mocked_mkdir.assert_called_with('username')
        mocked_uuid4.assert_called_with()
        mocked_file.save.assert_called_with('username/someguid')
        self.assertEqual(1, mocked_open.call_count)
        self.assertEqual(1, mocked_upload.call_count)
        mocked_mp3.assert_called_with('username/someguid')
        mocked_stat.assert_called_with('username/someguid')
        mocked_remove.assert_called_with('username/someguid')
        self.assertEqual('someguid', result[0])
        self.assertEqual('audio/mpeg', result[3])

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
