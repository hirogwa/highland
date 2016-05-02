import io
import unittest
import highland
from flask import json
from unittest.mock import MagicMock
from highland import models, show_operation, episode_operation, audio_operation,\
    user_operation


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

    def put_with_json(self, **kwargs):
        return self.app.put('/episode',
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
        episode = models.Episode(mocked_show, title, description,
                                 mocked_audio.id,
                                 models.Episode.DraftStatus.ready)
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

    @unittest.mock.patch.object(episode_operation, 'update')
    def test_put(self, mocked_update):
        show_id = 2
        episode_id = 3
        title = 'my new title'
        description = 'my new description'
        audio_id = 4

        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = show_id
        mocked_audio = MagicMock()
        mocked_audio.id = audio_id
        episode = models.Episode(mocked_show, title, description,
                                 mocked_audio.id,
                                 models.Episode.DraftStatus.ready)
        mocked_update.return_value = episode

        response = self.put_with_json(show_id=show_id,
                                      id=episode_id,
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

    @unittest.mock.patch.object(episode_operation, 'update')
    def test_put_input_check_show_id(self, mocked_update):
        with self.assertRaises(AssertionError):
            self.put_with_json(id=2,
                               title='new title',
                               description='new description',
                               audio_id=3)

    @unittest.mock.patch.object(episode_operation, 'update')
    def test_put_input_check_id(self, mocked_update):
        with self.assertRaises(AssertionError):
            self.put_with_json(show_id=1,
                               title='new title',
                               description='new description',
                               audio_id=3)

    @unittest.mock.patch.object(episode_operation, 'update')
    def test_put_input_check_title(self, mocked_update):
        with self.assertRaises(AssertionError):
            self.put_with_json(show_id=1,
                               id=2,
                               description='new description',
                               audio_id=3)

    @unittest.mock.patch.object(episode_operation, 'update')
    def test_put_input_check_description(self, mocked_update):
        with self.assertRaises(AssertionError):
            self.put_with_json(show_id=1,
                               id=2,
                               title='new title',
                               audio_id=3)

    @unittest.mock.patch.object(episode_operation, 'update')
    def test_put_input_check_audio_id(self, mocked_update):
        with self.assertRaises(AssertionError):
            self.put_with_json(show_id=1,
                               id=2,
                               title='new title',
                               description='new description')

    @unittest.mock.patch.object(episode_operation, 'load')
    def test_episodes_get(self, mocked_load):
        show_id = 2

        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = show_id
        mocked_audio_01 = MagicMock()
        mocked_audio_01.id = 10
        mocked_audio_02 = MagicMock()
        mocked_audio_02.id = 11
        episodes = [
            models.Episode(mocked_show, 'title01', 'desc01',
                           mocked_audio_01.id,
                           models.Episode.DraftStatus.ready),
            models.Episode(mocked_show, 'title02', 'desc02',
                           mocked_audio_02.id,
                           models.Episode.DraftStatus.draft)
        ]
        mocked_load.return_value = episodes

        response = self.app.get('/episodes/{}'.format(show_id))

        resp_data = json.loads(response.data)
        resp_episodes = resp_data.get('episodes')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(list(map(dict, episodes)), resp_episodes)


class TestAudio(unittest.TestCase):
    def setUp(self):
        highland.app.config['TESTING'] = True
        self.app = highland.app.test_client()

    @unittest.mock.patch.object(audio_operation, 'create')
    def test_post(self, mocked_create):
        mocked_user = MagicMock()
        mocked_user.id = 1
        filename = 'somefile.mp4'
        audio = models.Audio(mocked_user, filename)
        mocked_create.return_value = audio

        response = self.app.post(
            '/audio',
            data={
                'file': (io.BytesIO(b'test data'), filename)
            })

        resp_data = json.loads(response.data)
        resp_audio = resp_data.get('audio')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(dict(audio), resp_audio)

    @unittest.mock.patch.object(audio_operation, 'load')
    def test_get(self, mocked_load):
        mocked_user = MagicMock()
        mocked_user.id = 1
        audios = [
            models.Audio(mocked_user, 'testfile01.mp4'),
            models.Audio(mocked_user, 'testfile02.mp4')
        ]
        mocked_load.return_value = audios

        response = self.app.get('/audio')

        resp_data = json.loads(response.data)
        resp_audios = resp_data.get('audios')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(list(map(dict, audios)), resp_audios)


class TestUser(unittest.TestCase):
    def setUp(self):
        highland.app.config['TESTING'] = True
        self.app = highland.app.test_client()

    def post_with_json(self, **kwargs):
        return self.app.post('/user',
                             data=json.dumps(kwargs),
                             content_type='application/json')

    def put_with_json(self, **kwargs):
        return self.app.put('/user',
                            data=json.dumps(kwargs),
                            content_type='application/json')

    @unittest.mock.patch.object(user_operation, 'get')
    def test_get(self, mocked_get):
        id = 1
        user = models.User('username', 'email@example.com', 'some pass')
        user.id = id
        mocked_get.return_value = user

        response = self.app.get('/user/{}'.format(id))

        resp_data = json.loads(response.data)
        resp_user = resp_data.get('user')
        mocked_get.assert_called_with(id=id)
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(dict(user), resp_user)

    @unittest.mock.patch.object(user_operation, 'create')
    def test_post(self, mocked_create):
        username = 'some user'
        email = 'some@example.com'
        password = 'some pass'
        user = models.User(username, email, password)
        user.id = 1
        mocked_create.return_value = user

        response = self.post_with_json(
            username=username, email=email, password=password)

        resp_data = json.loads(response.data)
        resp_user = resp_data.get('user')
        mocked_create.assert_called_with(username, email, password)
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(dict(user), resp_user)

    @unittest.mock.patch.object(user_operation, 'create')
    def test_post_assert_input_username(self, mocked_create):
        with self.assertRaises(AssertionError):
            self.post_with_json(email='a@b.com', password='pass')
        mocked_create.assert_not_called()

    @unittest.mock.patch.object(user_operation, 'create')
    def test_post_assert_input_email(self, mocked_create):
        with self.assertRaises(AssertionError):
            self.post_with_json(username='name', password='pass')
        mocked_create.assert_not_called()

    @unittest.mock.patch.object(user_operation, 'create')
    def test_post_assert_input_password(self, mocked_create):
        with self.assertRaises(AssertionError):
            self.post_with_json(username='name', email='a@b.com')
        mocked_create.assert_not_called()

    @unittest.mock.patch.object(user_operation, 'update')
    def test_put(self, mocked_update):
        id = '1'
        username = 'some user'
        email = 'some@example.com'
        password = 'some pass'
        user = models.User(username, email, password)
        user.id = id
        mocked_update.return_value = user

        response = self.put_with_json(
            id=id, username=username, email=email, password=password)

        resp_data = json.loads(response.data)
        resp_user = resp_data.get('user')
        mocked_update.assert_called_with(int(id), username, email, password)
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(dict(user), resp_user)

    @unittest.mock.patch.object(user_operation, 'update')
    def test_put_assert_input_id(self, mocked_update):
        with self.assertRaises(AssertionError):
            self.put_with_json(username='some name',
                               email='some@example.com',
                               password='some pass')
        mocked_update.assert_not_called()

    @unittest.mock.patch.object(user_operation, 'update')
    def test_put_assert_input_username(self, mocked_update):
        with self.assertRaises(AssertionError):
            self.put_with_json(id='1',
                               email='some@example.com',
                               password='some pass')
        mocked_update.assert_not_called()

    @unittest.mock.patch.object(user_operation, 'update')
    def test_put_assert_input_email(self, mocked_update):
        with self.assertRaises(AssertionError):
            self.put_with_json(id='1',
                               username='some name',
                               password='some pass')
        mocked_update.assert_not_called()

    @unittest.mock.patch.object(user_operation, 'update')
    def test_put_assert_input_password(self, mocked_update):
        with self.assertRaises(AssertionError):
            self.put_with_json(id='1',
                               username='some name',
                               email='some@example.com')
        mocked_update.assert_not_called()
