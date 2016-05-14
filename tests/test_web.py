import datetime
import io
import unittest
import uuid
import highland
from flask import json
from unittest.mock import MagicMock
from highland import models, show_operation, episode_operation, audio_operation,\
    image_operation, user_operation


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
        subtitle = 'my subtitle'
        language = 'en-US'
        author = 'my author'
        category = 'my category'
        explicit = False

        mocked_user = MagicMock()
        mocked_user.id = 1
        show = models.Show(mocked_user, title, description, subtitle,
                           language, author, category, explicit)
        show.id = 2
        mocked_create.return_value = show

        response = self.post_with_json(
            title=title, description=description, subtitle=subtitle,
            language=language, author=author, category=category,
            explicit=str(explicit))

        resp_data = json.loads(response.data)
        resp_show = resp_data.get('show')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(show.owner_user_id, resp_show.get('owner_user_id'))
        self.assertEqual(show.id, resp_show.get('id'))
        self.assertEqual(show.title, resp_show.get('title'))
        self.assertEqual(show.description, resp_show.get('description'))
        self.assertEqual(show.subtitle, resp_show.get('subtitle'))
        self.assertEqual(show.language, resp_show.get('language'))
        self.assertEqual(show.author, resp_show.get('author'))
        self.assertEqual(show.category, resp_show.get('category'))
        self.assertEqual(show.explicit, resp_show.get('explicit'))

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
        subtitle = 'new subtitle'
        language = 'en-US'
        author = 'new author'
        category = 'new category'
        explicit = False

        mocked_user = MagicMock()
        mocked_user.id = 1
        show = models.Show(mocked_user, title, description, subtitle,
                           language, author, category, explicit)
        show.id = show_id
        mocked_update.return_value = show

        response = self.put_with_json(
            id=show_id, title=title, description=description,
            subtitle=subtitle, language=language, author=author,
            category=category, explicit=str(explicit))

        resp_data = json.loads(response.data)
        resp_show = resp_data.get('show')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(show.owner_user_id, resp_show.get('owner_user_id'))
        self.assertEqual(show.id, resp_show.get('id'))
        self.assertEqual(show.title, resp_show.get('title'))
        self.assertEqual(show.description, resp_show.get('description'))
        self.assertEqual(show.subtitle, resp_show.get('subtitle'))
        self.assertEqual(show.language, resp_show.get('language'))
        self.assertEqual(show.author, resp_show.get('author'))
        self.assertEqual(show.category, resp_show.get('category'))
        self.assertEqual(show.explicit, resp_show.get('explicit'))

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
            models.Show(
                mocked_user, 'title 01', 'description 01', 'subtitle 01',
                'en-US', 'author 01', 'category 01', False),
            models.Show(
                mocked_user, 'title 02', 'description 02', 'subtitle 02',
                'ja', 'author 02', 'category 02', True)
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
        draft_status = 'draft'
        scheduled_datetime = datetime.datetime.now(datetime.timezone.utc)
        title = 'my title'
        subtitle = 'my subtitle'
        description = 'my description'
        audio_id = 3
        explicit = True

        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = show_id
        mocked_audio = MagicMock()
        mocked_audio.id = audio_id
        episode = models.Episode(
            mocked_show, title, subtitle, description, mocked_audio.id,
            models.Episode.DraftStatus.draft, None, False)
        mocked_create.return_value = episode

        response = self.post_with_json(
            show_id=show_id,
            draft_status=draft_status,
            scheduled_datetime=scheduled_datetime.isoformat(),
            title=title,
            subtitle=subtitle,
            description=description,
            audio_id=audio_id,
            explicit=str(explicit))

        resp_data = json.loads(response.data)
        resp_episode = resp_data.get('episode')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(episode.owner_user_id,
                         resp_episode.get('owner_user_id'))
        self.assertEqual(episode.show_id, resp_episode.get('show_id'))
        self.assertEqual(episode.id, resp_episode.get('id'))
        self.assertEqual(episode.draft_status.name,
                         resp_episode.get('draft_status'))
        self.assertEqual(str(episode.scheduled_datetime),
                         resp_episode.get('scheduled_datetime'))
        self.assertEqual(episode.title, resp_episode.get('title'))
        self.assertEqual(episode.subtitle, resp_episode.get('subtitle'))
        self.assertEqual(episode.description, resp_episode.get('description'))
        self.assertEqual(episode.audio_id, resp_episode.get('audio_id'))
        self.assertEqual(episode.explicit, resp_episode.get('explicit'))

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
        draft_status = 'published'
        scheduled_datetime = datetime.datetime.now(datetime.timezone.utc)
        title = 'my new title'
        subtitle = 'my new subtitle'
        description = 'my new description'
        audio_id = 4
        explicit = True

        mocked_show = MagicMock()
        mocked_show.owner_user_id = 1
        mocked_show.id = show_id
        mocked_audio = MagicMock()
        mocked_audio.id = audio_id
        episode = models.Episode(
            mocked_show, title, subtitle, description, mocked_audio.id,
            models.Episode.DraftStatus.published, None, False)
        mocked_update.return_value = episode

        response = self.put_with_json(
            show_id=show_id,
            id=episode_id,
            draft_status=draft_status,
            scheduled_datetime=scheduled_datetime.isoformat(),
            title=title,
            subtitle=subtitle,
            description=description,
            audio_id=audio_id,
            explicit=str(explicit))

        resp_data = json.loads(response.data)
        resp_episode = resp_data.get('episode')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(episode.owner_user_id,
                         resp_episode.get('owner_user_id'))
        self.assertEqual(episode.show_id, resp_episode.get('show_id'))
        self.assertEqual(episode.id, resp_episode.get('id'))
        self.assertEqual(episode.draft_status.name,
                         resp_episode.get('draft_status'))
        self.assertEqual(str(episode.scheduled_datetime),
                         resp_episode.get('scheduled_datetime'))
        self.assertEqual(episode.title, resp_episode.get('title'))
        self.assertEqual(episode.subtitle, resp_episode.get('subtitle'))
        self.assertEqual(episode.description, resp_episode.get('description'))
        self.assertEqual(episode.audio_id, resp_episode.get('audio_id'))
        self.assertEqual(episode.explicit, resp_episode.get('explicit'))

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
            models.Episode(
                mocked_show, 'title01', 'sub01', 'desc01', mocked_audio_01.id,
                models.Episode.DraftStatus.published, None, False),
            models.Episode(
                mocked_show, 'title02', 'sub02', 'desc02', mocked_audio_02.id,
                models.Episode.DraftStatus.draft, None, False)
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
        duration = 1812
        length = 4000000
        type = 'audio/mpeg'
        guid = uuid.uuid4().hex
        audio = models.Audio(
            mocked_user, filename, duration, length, type, guid)
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
        guid01 = uuid.uuid4().hex
        guid02 = uuid.uuid4().hex
        audios = [
            models.Audio(
                mocked_user, 'f01.mp4', 1821, 4000000, 'audio/mpeg', guid01),
            models.Audio(
                mocked_user, 'f02.mp4', 1717, 3012012, 'audio/mpeg', guid02)
        ]
        mocked_load.return_value = audios

        response = self.app.get('/audio')

        resp_data = json.loads(response.data)
        resp_audios = resp_data.get('audios')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(list(map(dict, audios)), resp_audios)


class TestImage(unittest.TestCase):
    def setUp(self):
        highland.app.config['TESTING'] = True
        self.app = highland.app.test_client()

    @unittest.mock.patch.object(image_operation, 'create')
    def test_post(self, mocked_create):
        mocked_user = MagicMock()
        mocked_user.id = 1
        filename = 'somefile.jpg'
        guid = uuid.uuid4().hex
        image = models.Image(mocked_user, filename, guid)
        mocked_create.return_value = image

        response = self.app.post(
            '/image',
            data={
                'file': (io.BytesIO(b'test data'), filename)
            })

        resp_data = json.loads(response.data)
        resp_image = resp_data.get('image')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(dict(image), resp_image)

    @unittest.mock.patch.object(image_operation, 'load')
    def test_get(self, mocked_load):
        mocked_user = MagicMock()
        mocked_user.id = 1
        images = [
            models.Image(mocked_user, 'f01.jpg', uuid.uuid4().hex),
            models.Image(mocked_user, 'f02.jpg', uuid.uuid4().hex)
        ]
        mocked_load.return_value = images

        response = self.app.get('/image')

        resp_data = json.loads(response.data)
        resp_images = resp_data.get('images')
        self.assertEqual('success', resp_data.get('result'))
        self.assertEqual(list(map(dict, images)), resp_images)


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
        user = models.User('username', 'email@example.com', 'some pass',
                           'some name')
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
        name = 'Ultraman Taro'
        user = models.User(username, email, password, name)
        user.id = 1
        mocked_create.return_value = user

        response = self.post_with_json(
            username=username, email=email, password=password, name=name)

        resp_data = json.loads(response.data)
        resp_user = resp_data.get('user')
        mocked_create.assert_called_with(username, email, password, name)
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
        name = 'Ultraman Taro'
        user = models.User(username, email, password, name)
        user.id = id
        mocked_update.return_value = user

        response = self.put_with_json(
            id=id, username=username, email=email, password=password,
            name=name)

        resp_data = json.loads(response.data)
        resp_user = resp_data.get('user')
        mocked_update.assert_called_with(int(id), username, email, password,
                                         name)
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
