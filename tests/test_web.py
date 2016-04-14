import unittest
import highland
from flask import json
from unittest.mock import MagicMock
from highland import show_operation, models


class TestShow(unittest.TestCase):
    def setUp(self):
        highland.app.config['TESTING'] = True
        self.app = highland.app.test_client()

    def post_with_json(self, **kwargs):
        return self.app.post('/show',
                             data=json.dumps(kwargs),
                             content_type='application/json')

    def put_with_json(self, **kwargs):
        return self.app.put('/show',
                            data=json.dumps(kwargs),
                            content_type='application/json')

    @unittest.mock.patch.object(show_operation, 'create')
    def test_show_post(self, mocked_create):
        title = 'my title'
        description = 'my description'

        mocked_user = MagicMock()
        mocked_user.id = 1
        show = models.Show(mocked_user, title, description)
        show.id = 2
        mocked_create.return_value = show

        response = self.post_with_json(title=title, description=description)

        resp_data = json.loads(response.data)
        resp_show = resp_data.get('show')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(show.owner_user_id, resp_show.get('owner_user_id'))
        self.assertEqual(show.id, resp_show.get('id'))
        self.assertEqual(show.title, resp_show.get('title'))
        self.assertEqual(show.description, resp_show.get('description'))

    def test_show_post_input_check_title(self):
        with self.assertRaises(AssertionError):
            self.post_with_json(description='my description')

    def test_show_post_input_check_description(self):
        with self.assertRaises(AssertionError):
            self.post_with_json(title='my title')

    @unittest.mock.patch.object(show_operation, 'update')
    def test_show_put(self, mocked_update):
        show_id = 2
        title = 'new title'
        description = 'new description'

        mocked_user = MagicMock()
        mocked_user.id = 1
        show = models.Show(mocked_user, title, description)
        show.id = show_id
        mocked_update.return_value = show

        response = self.put_with_json(
            id=show_id, title=title, description=description)

        resp_data = json.loads(response.data)
        resp_show = resp_data.get('show')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(show.owner_user_id, resp_show.get('owner_user_id'))
        self.assertEqual(show.id, resp_show.get('id'))
        self.assertEqual(show.title, resp_show.get('title'))
        self.assertEqual(show.description, resp_show.get('description'))

    def test_show_put_input_check_id(self):
        with self.assertRaises(AssertionError):
            self.put_with_json(title='new title',
                               description='new description')

    def test_show_put_input_check_title(self):
        with self.assertRaises(AssertionError):
            self.put_with_json(id=2,
                               description='new description')

    def test_show_put_input_check_description(self):
        with self.assertRaises(AssertionError):
            self.put_with_json(id=2,
                               title='new title')
