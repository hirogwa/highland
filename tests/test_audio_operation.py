import uuid
import unittest
from unittest.mock import MagicMock
from highland import audio_operation, models, media_storage, settings


class TestAudioOperation(unittest.TestCase):
    @unittest.mock.patch.object(audio_operation, 'store_audio_data')
    @unittest.mock.patch('highland.models.Audio')
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    def test_create(self, mocked_add, mocked_commit, mocked_audio_class,
                    mocked_store):
        mocked_user = MagicMock()
        mocked_audio_file = MagicMock()

        guid = uuid.uuid4().hex
        duration = 1200
        length = 19000000
        type = 'audio/mpeg'
        mocked_store.return_value = guid, duration, length, type

        mocked_audio = MagicMock()
        mocked_audio_class.return_value = mocked_audio

        result = audio_operation.create(mocked_user, mocked_audio_file)

        mocked_store.assert_called_with(mocked_user, mocked_audio_file)
        mocked_add.assert_called_with(mocked_audio)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_audio, result)

    @unittest.mock.patch.object(media_storage, 'delete')
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'delete')
    @unittest.mock.patch.object(audio_operation, 'get_audio_or_assert')
    def test_delete(self, mocked_get_audio, mocked_delete, mocked_commit,
                    mocked_media_delete):
        mocked_audio = MagicMock()
        mocked_user = MagicMock()
        audio_ids = [2]
        mocked_get_audio.return_value = mocked_audio

        result = audio_operation.delete(mocked_user, audio_ids)

        mocked_get_audio.assert_called_with(mocked_user, audio_ids[0])
        mocked_media_delete.assert_called_with(mocked_audio.guid,
                                               settings.S3_BUCKET_AUDIO,
                                               mocked_user.username)
        mocked_delete.assert_called_with(mocked_audio)
        mocked_commit.assert_called_with()
        self.assertTrue(result)

    @unittest.mock.patch('highland.models.Audio.query')
    def test_load(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1

        mocked_audio_01 = MagicMock()
        mocked_audio_02 = MagicMock()
        audio_list = [mocked_audio_01, mocked_audio_02]

        mocked_filter = MagicMock()
        mocked_filter.all.return_value = audio_list
        mocked_query.filter_by.return_value = mocked_filter

        result = audio_operation.load(mocked_user)

        mocked_query.filter_by.assert_called_with(owner_user_id=mocked_user.id)
        mocked_filter.all.assert_called_with()
        self.assertEqual(audio_list, result)

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

        result = audio_operation.get_audio_or_assert(
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
            audio_operation.get_audio_or_assert(
                mocked_user, audio_id)
