import unittest
import highland
from flask import json
from unittest.mock import MagicMock
from highland import show_operation, episode_operation, models


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

    @unittest.mock.patch.object(show_operation, 'load')
    def test_show_get(self, mocked_load):
        mocked_user = MagicMock()
        mocked_user.id = 1
        shows = [
            models.Show(mocked_user, 'title 01', 'description 01'),
            models.Show(mocked_user, 'title 02', 'description 02')
        ]
        mocked_load.return_value = shows

        response = self.app.get('/show')

        resp_data = json.loads(response.data)
        resp_shows = resp_data.get('shows')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(list(map(dict, shows)), resp_shows)


class TestEpisode(unittest.TestCase):
    def setUp(self):
        highland.app.config['TESTING'] = True
        self.app = highland.app.test_client()

    def post_with_json(self, **kwargs):
        return self.app.post('/episode',
                             data=json.dumps(kwargs),
                             content_type='application/json')

    @unittest.mock.patch.object(episode_operation, 'create')
    def test_post(self, mocked_create):
        show_id = 2
        title = 'my title'
        description = 'my description'
        audio_id = 3

        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = show_id
        mocked_audio = MagicMock()
        mocked_audio.id = audio_id
        episode = models.Episode(mocked_show, title, description, mocked_audio)
        mocked_create.return_value = episode

        response = self.post_with_json(show_id=show_id,
                                       title=title,
                                       description=description,
                                       audio_id=audio_id)

        resp_data = json.loads(response.data)
        resp_episode = resp_data.get('episode')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(episode.owner_user_id,
                         resp_episode.get('owner_user_id'))
        self.assertEqual(episode.show_id, resp_episode.get('show_id'))
        self.assertEqual(episode.id, resp_episode.get('id'))
        self.assertEqual(episode.title, resp_episode.get('title'))
        self.assertEqual(episode.description, resp_episode.get('description'))
        self.assertEqual(episode.audio_id, resp_episode.get('audio_id'))

    @unittest.mock.patch.object(episode_operation, 'create')
    def test_post_input_check_show_id(self, mocked_create):
        with self.assertRaises(AssertionError):
            self.post_with_json(title='new title',
                                description='new description',
                                audio_id=3)

    @unittest.mock.patch.object(episode_operation, 'create')
    def test_post_input_check_title(self, mocked_create):
        with self.assertRaises(AssertionError):
            self.post_with_json(show_id=2,
                                description='new description',
                                audio_id=3)

    @unittest.mock.patch.object(episode_operation, 'create')
    def test_post_input_check_description(self, mocked_create):
        with self.assertRaises(AssertionError):
            self.post_with_json(show_id=2,
                                title='new title',
                                audio_id=3)

    @unittest.mock.patch.object(episode_operation, 'create')
    def test_post_input_check_audio_id(self, mocked_create):
        with self.assertRaises(AssertionError):
            self.post_with_json(show_id=2,
                                title='new title',
                                description='new description')
