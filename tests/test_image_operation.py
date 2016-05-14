import uuid
import unittest
from unittest.mock import MagicMock
from highland import media_storage, image_operation, models


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
        mocked_store.return_value = guid

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
            mocked_image.guid, image_operation.IMAGE_FOLDER)
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

    @unittest.mock.patch.object(uuid, 'uuid4')
    @unittest.mock.patch.object(media_storage, 'upload')
    def test_store_image_data(self, mocked_upload, mocked_uuid4):
        mocked_image = MagicMock()
        guid = 'test_guid'
        mocked_uuid = MagicMock()
        mocked_uuid.hex = guid
        mocked_uuid4.return_value = mocked_uuid

        result = image_operation.store_image_data(1, mocked_image)

        mocked_upload.assert_called_with(mocked_image, guid,
                                         image_operation.IMAGE_FOLDER)
        self.assertEqual(guid, result)
