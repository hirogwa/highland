import unittest
from unittest.mock import MagicMock
from highland import audio_operation, models, media_storage


class TestAudioOperation(unittest.TestCase):
    @unittest.mock.patch.object(media_storage, 'upload')
    @unittest.mock.patch('highland.models.Audio')
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    def test_create(self, mocked_add, mocked_commit, mocked_audio_class,
                    mocked_upload):
        mocked_user = MagicMock()
        mocked_audio_file = MagicMock()

        mocked_audio = MagicMock()
        mocked_audio_class.return_value = mocked_audio

        result = audio_operation.create(mocked_user, mocked_audio_file)

        mocked_upload.assert_called_with(mocked_audio_file,
                                         audio_operation.AUDIO_FOLDER)
        mocked_add.assert_called_with(mocked_audio)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_audio, result)

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'delete')
    def test_delete(self, mocked_delete, mocked_commit):
        mocked_audio = MagicMock()

        result = audio_operation.delete(mocked_audio)

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
