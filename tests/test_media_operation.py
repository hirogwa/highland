import unittest
from unittest.mock import patch, MagicMock

from tests.utility import assign_ids, create_user
from highland import media_storage, media_operation
from highland.exception import AccessNotAllowedError
from highland.models import db, Audio, User


class TestMediaOperation(unittest.TestCase):
    @patch.object(media_storage, 'delete')
    @patch.object(db, 'session')
    def test_delete(self, mock_session, mock_delete):
        audios = [
            Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01'),
            Audio(1, 'file_two', 60, 256, 'audio/mpeg', 'some_guid_02')
        ]
        mock_key_fn = MagicMock()
        mock_key_fn.side_effect = \
            lambda user, media: '{}+{}'.format(user, media)
        mock_bucket = MagicMock()
        self._delete_prep(mock_session, audios, Audio)

        media_operation.delete(
            1, [x.id for x in audios], Audio, mock_key_fn, mock_bucket)

        self.assertEqual(2, mock_key_fn.call_count)
        self.assertEqual(2, mock_delete.call_count)
        mock_session.commit.assert_called_with()
        self.assertEqual(2, mock_session.delete.call_count)
        mock_session.commit.assert_called_with()

    @patch.object(media_storage, 'delete')
    @patch.object(db, 'session')
    def test_delete_raises_when_audio_is_not_owned_by_the_user(
            self, mock_session, mock_delete):
        audios = [
            Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01'),
            Audio(9, 'file_two', 60, 256, 'audio/mpeg', 'some_guid_02')
        ]
        self._delete_prep(mock_session, audios, Audio)

        with self.assertRaises(AccessNotAllowedError):
            media_operation.delete(
                9, [x.id for x in audios], Audio, MagicMock(), MagicMock())

        mock_delete.assert_not_called()
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch.object(media_storage, 'delete')
    @patch.object(db, 'session')
    def test_delete_db_record_is_not_deleted_when_storage_error(
            self, mock_session, mock_delete):
        audio = Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01')
        self._delete_prep(mock_session, [audio], Audio)
        mock_delete.side_effect = ValueError

        media_operation.delete(1, [audio.id], Audio, MagicMock(), MagicMock())

        self.assertEqual(1, mock_delete.call_count)
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_called_with()

    def _delete_prep(self, mock_session, medias, model_class):
        medias = assign_ids(medias, 10)
        media_ids = [x.id for x in medias]
        users = [create_user(media.owner_user_id) for media in medias]
        mock_session.query(model_class, User).join(User). \
            filter(model_class.id.in_(media_ids)). \
            order_by(model_class.owner_user_id). \
            all.return_value = [(x, y) for x, y in zip(medias, users)]
