import unittest
from unittest.mock import patch

from tests.utility import create_user, assign_ids
from highland import app, audio_operation, media_operation, user_operation
from highland.exception import NoSuchEntityError
from highland.models import db, Audio, Episode


class TestAudioOperation(unittest.TestCase):
    @patch.object(db.session, 'commit')
    @patch.object(db.session, 'add')
    @patch('uuid.uuid4')
    def test_create(self, mock_uuid4, mock_add, mock_commit):
        mock_uuid4.return_value.hex = 'some_guid'

        result = audio_operation.create(1, 'some.mp3', 120, 6400, 'audio/mpeg')

        self.assertEqual(1, mock_add.call_count)
        mock_commit.assert_called_with()
        self.assertEqual(1, result.get('owner_user_id'))
        self.assertEqual('some_guid', result.get('guid'))

    @patch.object(app, 'config')
    @patch.object(media_operation, 'delete')
    def test_delete(self, mock_media_delete, mock_config):
        mock_config.get.side_effect = \
            lambda key: 'some_bucket' if key == 'S3_BUCKET_AUDIO' else None
        audio_operation.delete(1, [10, 11, 12])

        mock_media_delete.assert_called_with(
            user_id=1, media_ids=[10, 11, 12], model_class=Audio,
            get_key=audio_operation._get_audio_key, bucket='some_bucket'
        )

    @patch.object(audio_operation, 'get_audio_url')
    @patch.object(user_operation, 'get_model')
    @patch.object(db, 'session')
    def test_load(self, mock_session, mock_get_user, mock_get_url):
        user = create_user(id=1)
        audios = [
            Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01'),
            Audio(1, 'file_two', 60, 256, 'audio/mpeg', 'some_guid_02')
        ]
        audios, episodes, mock_audio_query = \
            self._load_prep(audios, mock_session, user.id)
        episodes[1] = None

        mock_audio_query.all.return_value = \
            ((a, e) for a, e in zip(audios, episodes))

        mock_get_user.return_value = user
        mock_get_url.return_value = 'some_url'

        one, two = audio_operation.load(user.id)

        self.assertEqual(1, one.get('owner_user_id'))
        self.assertEqual(1, two.get('owner_user_id'))
        self.assertEqual('file_one', one.get('filename'))
        self.assertEqual('file_two', two.get('filename'))
        self.assertEqual(11, one.get('show_id'))
        self.assertEqual(20, one.get('episode_id'))
        self.assertIsNone(two.get('show_id'))
        self.assertIsNone(two.get('episode_id'))

    @patch.object(audio_operation, 'get_audio_url')
    @patch.object(user_operation, 'get_model')
    @patch.object(Episode, 'query')
    @patch.object(db, 'session')
    def test_load_loads_unused_only_when_unused_only_is_set(
            self, mock_session, mock_episode_query, mock_get_user,
            mock_get_url):
        user = create_user(id=1)
        audios = [
            Audio(1, 'whitelisted', 30, 128, 'audio/mpeg', 'some_guid_01'),
            Audio(1, 'unused', 60, 256, 'audio/mpeg', 'some_guid_02'),
            Audio(1, 'used', 90, 512, 'audio/mpeg', 'some_guid_03')
        ]
        audios, episodes, mock_audio_query = \
            self._load_prep(audios, mock_session, user.id)

        mock_episode_query. \
            filter_by(owner_user_id=user.id). \
            filter(Episode.audio_id.isnot(None)). \
            filter(Episode.audio_id != audios[0].id) .\
            all.return_value = episodes[2:]
        mock_audio_query. \
            filter(Audio.id.notin_(x.audio_id for x in episodes[2:])). \
            all. \
            return_value = ((a, e) for a, e in zip(audios[:2], episodes[:2]))

        result = audio_operation.load(
            user.id, unused_only=True, whitelisted_id=audios[0].id)

        self.assertEqual(2, len(result))
        self.assertEqual('whitelisted', result[0].get('filename'))
        self.assertEqual('unused', result[1].get('filename'))

    def _load_prep(self, audios, mock_session, user_id):
        audios = assign_ids(audios, 10)
        episodes = []
        for audio in audios:
            episodes.append(Episode(
                show_id=11, user_id=user_id, title='some ep', subtitle='sub',
                description='desc', audio_id=audio.id, draft_status=None,
                scheduled_datetime=None, explicit=False, image_id=None,
                alias='alias')
            )
        assign_ids(episodes, 20)

        mock_audio_query = mock_session. \
            query(Audio, Episode). \
            outerjoin(Episode). \
            filter(Audio.owner_user_id == user_id)

        return audios, episodes, mock_audio_query

    @patch.object(Audio, 'query')
    def test_get(self, mock_query):
        audio = Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01')
        mock_query.filter_by.return_value.first.return_value = audio
        self.assertEqual(audio, audio_operation.get(audio.id))

    @patch.object(Audio, 'query')
    def test_get_raises_when_audio_not_found(self, mock_query):
        mock_query.filter_by.return_value.first.return_value = None
        with self.assertRaises(NoSuchEntityError):
            audio_operation.get(1)

    @patch('highland.app.config')
    def test_get_audio_url(self, mock_config):
        user = create_user(1)
        audio = Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01')
        mock_config.get.return_value = 'http://somehost.com'

        self.assertEqual(
            'http://somehost.com/identity/some_guid_01',
            audio_operation.get_audio_url(user, audio))

    def test_get_audio_url_raises_if_user_is_incorrect(self):
        user = create_user(9)
        audio = Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01')
        with self.assertRaises(ValueError):
            audio_operation.get_audio_url(user, audio)
