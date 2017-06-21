import unittest
from unittest.mock import patch, MagicMock
from highland import media_storage, image_operation, models, settings, \
    exception
from highland.models import db


class TestImageOperation(unittest.TestCase):
    @patch.object(db, 'session')
    @patch('uuid.uuid4')
    def test_create(self, mock_uuid4, mock_session):
        mock_uuid4.return_value.hex = 'some_guid'

        result = image_operation.create(1, 'file.jpg', 'image/jpeg')

        self.assertEqual(1, mock_session.add.call_count)
        mock_session.commit.assert_called_with()
        self.assertEqual(1, result.get('owner_user_id'))
        self.assertEqual('some_guid', result.get('guid'))

    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'delete')
    @patch.object(media_storage, 'delete')
    @patch.object(image_operation, 'get_image_or_assert')
    def test_delete(self, mock_get, mock_storage_delete, mock_db_delete,
                    mock_db_commit):
        mock_user, mock_image_01, mock_image_02 = \
            MagicMock(), MagicMock(), MagicMock()
        mock_user.identity_id = 'identity_id'
        mock_image_02.guid = 'non-existing'
        mock_get.side_effect = \
            lambda u, i: mock_image_01 if i == 1 else mock_image_02

        def f(key, bucket, folder=''):
            if key == 'identity_id/non-existing':
                raise ValueError()
            else:
                return mock_image_01
        mock_storage_delete.side_effect = f

        result = image_operation.delete(mock_user, [1, 2])

        self.assertEqual(2, mock_get.call_count)
        self.assertEqual(2, mock_storage_delete.call_count)
        self.assertEqual(1, mock_db_delete.call_count)
        mock_db_delete.assert_called_with(mock_image_01)
        mock_db_commit.assert_called_with()
        self.assertTrue(result)

    @patch('highland.models.Image.query')
    def test_load(self, mock_query):
        mock_user = MagicMock()
        image_list = [MagicMock(), MagicMock()]
        mock_filter = MagicMock()
        mock_filter.all.return_value = image_list
        mock_query.filter_by.return_value = mock_filter

        result = image_operation.load(mock_user)

        mock_query.filter_by.assert_called_with(owner_user_id=mock_user.id)
        mock_filter.all.assert_called_with()
        self.assertEqual(image_list, result)

    @patch('highland.models.Image.query')
    def test_get_image_or_assert(self, mock_query):
        mock_user, mock_image = MagicMock(), MagicMock()
        mock_image.owner_user_id = mock_user.id

        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_image
        mock_query.filter_by.return_value = mock_filter

        result = image_operation.get_image_or_assert(
            mock_user, mock_image.id)

        mock_query.filter_by.assert_called_with(
            owner_user_id=mock_user.id, id=mock_image.id)
        mock_filter.first.assert_called_with()
        self.assertEqual(mock_image, result)

    @patch('highland.models.Image.query')
    def test_get_image_or_assert_assert(self, mock_query):
        mock_user = MagicMock()

        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter

        with self.assertRaises(exception.NoSuchEntityError):
            image_operation.get_image_or_assert(mock_user, 1)

    @patch.object(image_operation, 'access_allowed_or_raise')
    def test_get_image_url(self, mock_access):
        mock_user, mock_image = MagicMock(), MagicMock()
        mock_user.identity_id = 'identity_id'
        mock_image.guid = 'someguid'

        result = image_operation.get_image_url(mock_user, mock_image)

        mock_access.assert_called_with(mock_user.id, mock_image)
        self.assertEqual('{}/{}'.format(
            settings.HOST_IMAGE, 'identity_id/someguid'), result)

    def test_access_allowed_or_raise(self):
        mock_image = MagicMock()
        mock_image.owner_user_id = 1

        result = image_operation.access_allowed_or_raise(1, mock_image)

        self.assertEqual(mock_image, result)

    def test_access_allowed_or_raise_raise(self):
        mock_image = MagicMock()
        mock_image.owner_user_id = 1
        with self.assertRaises(exception.AccessNotAllowedError):
            image_operation.access_allowed_or_raise(2, mock_image)
