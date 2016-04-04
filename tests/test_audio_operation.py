import unittest
from unittest.mock import MagicMock
from highland import audio_operation, models


class TestAudioOperation(unittest.TestCase):
    @unittest.mock.patch('highland.models.Audio')
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    def test_create(self, mocked_add, mocked_commit, mocked_audio_class):
        mocked_user = MagicMock()
        mocked_audio_file = MagicMock()

        mocked_audio = MagicMock()
        mocked_audio_class.return_value = mocked_audio

        result = audio_operation.create(mocked_user, mocked_audio_file)

        mocked_add.assert_called_with(mocked_audio)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_audio, result)
