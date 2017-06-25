import unittest
from unittest.mock import patch

from tests.utility import assign_ids, create_user
from highland import app, image_operation, media_operation, user_operation
from highland.exception import NoSuchEntityError
from highland.models import db, Image


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

    @patch.object(app, 'config')
    @patch.object(media_operation, 'delete')
    def test_delete(self, mock_media_delete, mock_config):
        mock_config.get.side_effect = \
            lambda key: 'some_bucket' if key == 'S3_BUCKET_IMAGE' else None
        image_operation.delete(1, [10, 11, 12])

        mock_media_delete.assert_called_with(
            user_id=1, media_ids=[10, 11, 12], model_class=Image,
            get_key=image_operation._get_image_key, bucket='some_bucket'
        )

    @patch.object(Image, 'query')
    @patch.object(user_operation, 'get_model')
    def test_load(self, mock_get_user, mock_query):
        mock_get_user.return_value = create_user(1)
        images = [
            Image(1, 'one.jpeg', 'guid_one', 'image/jpeg'),
            Image(1, 'two.jpeg', 'guid_two', 'image/jpeg')
        ]
        mock_query.filter_by.return_value.all.return_value = images

        result = image_operation.load(1)

        self.assertEqual(2, len(result))
        self.assertEqual('one.jpeg', result[0].get('filename'))
        self.assertEqual('two.jpeg', result[1].get('filename'))
        self.assertTrue(result[0].get('url'))
        self.assertTrue(result[1].get('url'))

    @patch.object(user_operation, 'get_model')
    @patch.object(image_operation, 'get_model')
    def test_get(self, mock_get_model, mock_get_user):
        image = Image(1, 'one.jpeg', 'guid_one', 'image/jpeg')
        assign_ids([image], 10)
        mock_get_model.return_value = image
        mock_get_user.return_value = create_user(1)

        result = image_operation.get(1, 10)

        self.assertEqual(10, result.get('id'))
        self.assertEqual('one.jpeg', result.get('filename'))
        self.assertTrue(result.get('url'))

    @patch.object(Image, 'query')
    def test_get_model(self, mock_query):
        image = Image(1, 'one.jpeg', 'guid_one', 'image/jpeg')
        assign_ids([image], 10)
        mock_query.filter_by.return_value.first.return_value = image
        self.assertEqual(image, image_operation.get_model(10))

    @patch.object(Image, 'query')
    def test_get_model_raises_when_image_not_found(self, mock_query):
        mock_query.filter_by.return_value.first.return_value = None
        with self.assertRaises(NoSuchEntityError):
            image_operation.get_model(10)

    @patch.object(app, 'config')
    def test_get_image_url(self, mock_config):
        user = create_user(1)
        image = Image(1, 'one.jpeg', 'guid_one', 'image/jpeg')
        mock_config.get.side_effect = \
            lambda key: 'http://somehost.com' if key == 'HOST_IMAGE' else None

        self.assertEqual('http://somehost.com/identity/guid_one',
                         image_operation.get_image_url(user, image))
