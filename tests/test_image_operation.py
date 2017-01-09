import unittest
from unittest.mock import patch, MagicMock
from highland import media_storage, image_operation, models, settings, \
    exception


class TestImageOperation(unittest.TestCase):
    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'add')
    @patch('highland.models.Image')
    @patch('uuid.uuid4')
    def test_create(
            self, mocked_uuid4, mocked_image_class, mocked_add, mocked_commit):
        mocked_user = MagicMock()
        mocked_image = MagicMock()
        mocked_image_class.return_value = mocked_image

        mocked_uuid = MagicMock()
        mocked_uuid4.return_value = mocked_uuid

        result = image_operation.create(mocked_user, 'file.jpg', 'image/jpeg')

        mocked_add.assert_called_with(mocked_image)
        mocked_commit.assert_called_with()
        mocked_image_class.assert_called_with(
            mocked_user, 'file.jpg', mocked_uuid.hex, 'image/jpeg')
        self.assertEqual(mocked_image, result)

    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'delete')
    @patch.object(media_storage, 'delete')
    @patch.object(image_operation, 'get_image_or_assert')
    def test_delete(self, mocked_get, mocked_storage_delete, mocked_db_delete,
                    mocked_db_commit):
        mocked_user, mocked_image_01, mocked_image_02 = \
            MagicMock(), MagicMock(), MagicMock()
        mocked_user.identity_id = 'identity_id'
        mocked_image_02.guid = 'non-existing'
        mocked_get.side_effect = \
            lambda u, i: mocked_image_01 if i == 1 else mocked_image_02

        def f(key, bucket, folder=''):
            if key == 'identity_id/non-existing':
                raise ValueError()
            else:
                return mocked_image_01
        mocked_storage_delete.side_effect = f

        result = image_operation.delete(mocked_user, [1, 2])

        self.assertEqual(2, mocked_get.call_count)
        self.assertEqual(2, mocked_storage_delete.call_count)
        self.assertEqual(1, mocked_db_delete.call_count)
        mocked_db_delete.assert_called_with(mocked_image_01)
        mocked_db_commit.assert_called_with()
        self.assertTrue(result)

    @patch('highland.models.Image.query')
    def test_load(self, mocked_query):
        mocked_user = MagicMock()
        image_list = [MagicMock(), MagicMock()]
        mocked_filter = MagicMock()
        mocked_filter.all.return_value = image_list
        mocked_query.filter_by.return_value = mocked_filter

        result = image_operation.load(mocked_user)

        mocked_query.filter_by.assert_called_with(owner_user_id=mocked_user.id)
        mocked_filter.all.assert_called_with()
        self.assertEqual(image_list, result)

    @patch('highland.models.Image.query')
    def test_get_image_or_assert(self, mocked_query):
        mocked_user, mocked_image = MagicMock(), MagicMock()
        mocked_image.owner_user_id = mocked_user.id

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_image
        mocked_query.filter_by.return_value = mocked_filter

        result = image_operation.get_image_or_assert(
            mocked_user, mocked_image.id)

        mocked_query.filter_by.assert_called_with(
            owner_user_id=mocked_user.id, id=mocked_image.id)
        mocked_filter.first.assert_called_with()
        self.assertEqual(mocked_image, result)

    @patch('highland.models.Image.query')
    def test_get_image_or_assert_assert(self, mocked_query):
        mocked_user = MagicMock()

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(exception.NoSuchEntityError):
            image_operation.get_image_or_assert(mocked_user, 1)

    @patch.object(image_operation, 'access_allowed_or_raise')
    def test_get_image_url(self, mocked_access):
        mocked_user, mocked_image = MagicMock(), MagicMock()
        mocked_user.identity_id = 'identity_id'
        mocked_image.guid = 'someguid'

        result = image_operation.get_image_url(mocked_user, mocked_image)

        mocked_access.assert_called_with(mocked_user.id, mocked_image)
        self.assertEqual('{}/{}'.format(
            settings.HOST_IMAGE, 'identity_id/someguid'), result)

    def test_access_allowed_or_raise(self):
        mocked_image = MagicMock()
        mocked_image.owner_user_id = 1

        result = image_operation.access_allowed_or_raise(1, mocked_image)

        self.assertEqual(mocked_image, result)

    def test_access_allowed_or_raise_raise(self):
        mocked_image = MagicMock()
        mocked_image.owner_user_id = 1
        with self.assertRaises(exception.AccessNotAllowedError):
            image_operation.access_allowed_or_raise(2, mocked_image)
