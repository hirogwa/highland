import unittest
from unittest.mock import MagicMock
from highland import media_storage, image_operation, models, settings


class TestImageOperation(unittest.TestCase):
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    @unittest.mock.patch('highland.models.Image')
    @unittest.mock.patch.object(image_operation, 'store_image_data')
    def test_create(self, mocked_store, mocked_image_class, mocked_add,
                    mocked_commit):
        mocked_user = MagicMock()
        mocked_image_file = MagicMock()
        guid = 'some guid'
        type = 'jpeg'
        mocked_store.return_value = guid, type

        mocked_image = MagicMock()
        mocked_image_class.return_value = mocked_image

        result = image_operation.create(mocked_user, mocked_image_file)

        mocked_store.assert_called_with(mocked_user.id, mocked_image_file)
        mocked_add.assert_called_with(mocked_image)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_image, result)

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'delete')
    @unittest.mock.patch.object(media_storage, 'delete')
    def test_delete(self, mocked_storage_delete, mocked_db_delete,
                    mocked_db_commit):
        mocked_image = MagicMock()

        result = image_operation.delete(mocked_image)

        mocked_storage_delete.assert_called_with(
            mocked_image.guid, settings.S3_BUCKET_IMAGE)
        mocked_db_delete.assert_called_with(mocked_image)
        mocked_db_commit.assert_called_with()
        self.assertTrue(result)

    @unittest.mock.patch('highland.models.Image.query')
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

    @unittest.mock.patch('highland.models.Image.query')
    def test_get_image_or_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        mocked_image = MagicMock()
        mocked_image.owner_user_id = mocked_user.id
        mocked_image.id = 2

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_image
        mocked_query.filter_by.return_value = mocked_filter

        result = image_operation.get_image_or_assert(
            mocked_user, mocked_image.id)

        mocked_query.filter_by.assert_called_with(owner_user_id=mocked_user.id,
                                                  id=mocked_image.id)
        mocked_filter.first.assert_called_with()
        self.assertEqual(mocked_image, result)

    @unittest.mock.patch('highland.models.Image.query')
    def test_get_image_or_assert_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        image_id = 2

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(AssertionError):
            image_operation.get_image_or_assert(
                mocked_user, image_id)
