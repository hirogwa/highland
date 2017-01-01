import datetime
import io
import unittest
import uuid
import highland
from flask import json
from unittest.mock import MagicMock
from highland import models, show_operation, episode_operation, audio_operation,\
    image_operation, user_operation


class AuthMixin(object):
    def assertForbidden(self, response):
        self.assertEqual(403, response.status_code)


class TestShow(unittest.TestCase, AuthMixin):
    def setUp(self):
        highland.app.config['TESTING'] = True
        self.app = highland.app.test_client()

    def post_with_json(self, **kwargs):
        return self.app.post(
            '/show', data=json.dumps(kwargs), content_type='application/json')

    def put_with_json(self, **kwargs):
        return self.app.put(
            '/show', data=json.dumps(kwargs), content_type='application/json')

    def test_show_post(self):
        self.assertForbidden(self.post_with_json())

    def test_show_put(self):
        self.assertForbidden(self.put_with_json())

    def test_show_get(self):
        self.assertForbidden(self.app.get('/show'))
        self.assertForbidden(self.app.get('/show/1'))


class TestEpisode(unittest.TestCase, AuthMixin):
    def setUp(self):
        highland.app.config['TESTING'] = True
        self.app = highland.app.test_client()

    def post_with_json(self, **kwargs):
        return self.app.post(
            '/episode', data=json.dumps(kwargs),
            content_type='application/json')

    def put_with_json(self, **kwargs):
        return self.app.put(
            '/episode', data=json.dumps(kwargs),
            content_type='application/json')

    def test_post(self):
        self.assertForbidden(self.post_with_json())

    def test_put(self):
        self.assertForbidden(self.put_with_json())

    def test_episodes_get(self):
        self.assertForbidden(self.app.get('/episodes/1'))


class TestAudio(unittest.TestCase, AuthMixin):
    def setUp(self):
        highland.app.config['TESTING'] = True
        self.app = highland.app.test_client()

    def test_post(self):
        self.assertForbidden(self.app.post('/audio'))

    def test_get(self):
        self.assertForbidden(self.app.get('/audio'))


class TestImage(unittest.TestCase, AuthMixin):
    def setUp(self):
        highland.app.config['TESTING'] = True
        self.app = highland.app.test_client()

    def test_post(self):
        self.assertForbidden(self.app.post('/image'))

    def test_get(self):
        self.assertForbidden(self.app.get('/image'))
