import unittest
from unittest.mock import patch, MagicMock
from highland import audio_operation, models, media_storage, settings, \
    exception, user_operation
from highland.exception import AccessNotAllowedError
from highland.models import Audio, Episode, User


class TestAudioOperation(unittest.TestCase):
    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'add')
    @patch('uuid.uuid4')
    def test_create(self, mock_uuid4, mock_add, mock_commit):
        mock_uuid4.return_value.hex = 'some_guid'

        result = audio_operation.create(1, 'some.mp3', 120, 6400, 'audio/mpeg')

        self.assertEqual(1, mock_add.call_count)
        mock_commit.assert_called_with()
        self.assertEqual(1, result.get('owner_user_id'))
        self.assertEqual('some_guid', result.get('guid'))

    @patch.object(media_storage, 'delete')
    @patch.object(models.db, 'session')
    def test_delete(self, mock_session, mock_delete):
        audios = [
            Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01'),
            Audio(1, 'file_two', 60, 256, 'audio/mpeg', 'some_guid_02')
        ]
        self._delete_prep(mock_session, audios)

        audio_operation.delete(1, [x.id for x in audios])

        self.assertEqual(2, mock_delete.call_count)
        mock_session.commit.assert_called_with()

    @patch.object(media_storage, 'delete')
    @patch.object(models.db, 'session')
    def test_delete_raises_when_audio_is_not_owned_by_the_user(
            self, mock_session, mock_delete):
        audios = [
            Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01'),
            Audio(9, 'file_two', 60, 256, 'audio/mpeg', 'some_guid_02')
        ]
        self._delete_prep(mock_session, audios)

        with self.assertRaises(AccessNotAllowedError):
            audio_operation.delete(9, [x.id for x in audios])

        mock_delete.assert_not_called()
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch.object(media_storage, 'delete')
    @patch.object(models.db, 'session')
    def test_delete_db_record_is_not_deleted_when_storage_error(
            self, mock_session, mock_delete):
        audio = Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01')
        self._delete_prep(mock_session, [audio])
        mock_delete.side_effect = ValueError

        audio_operation.delete(1, [audio.id])

        self.assertEqual(1, mock_delete.call_count)
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_called_with()

    def _create_user(self, id):
        user = User('username', 'name', 'identity')
        user.id = id
        return user

    def _assign_ids(self, entities, base):
        for x in entities:
            x.id = base
            base += 1
        return entities

    def _delete_prep(self, mock_session, audios):
        audios = self._assign_ids(audios, 10)
        audio_ids = [x.id for x in audios]
        users = [self._create_user(audio.owner_user_id) for audio in audios]
        mock_session.query(Audio, User).join(User). \
            filter(Audio.id.in_(audio_ids)).order_by(Audio.owner_user_id). \
            all.return_value = [(x, y) for x, y in zip(audios, users)]

    @patch.object(audio_operation, 'get_audio_url')
    @patch.object(user_operation, 'get_model')
    @patch.object(models.db, 'session')
    def test_load(self, mock_session, mock_get_user, mock_get_url):
        user = self._create_user(id=1)
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
    @patch('highland.models.Episode.query')
    @patch.object(models.db, 'session')
    def test_load_loads_unused_only_when_unused_only_is_set(
            self, mock_session, mock_episode_query, mock_get_user,
            mock_get_url):
        user = self._create_user(id=1)
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
        audios = self._assign_ids(audios, 10)
        episodes = []
        for audio in audios:
            episodes.append(Episode(
                show_id=11, user_id=user_id, title='some ep', subtitle='sub',
                description='desc', audio_id=audio.id, draft_status=None,
                scheduled_datetime=None, explicit=False, image_id=None,
                alias='alias')
            )
        self._assign_ids(episodes, 20)

        mock_audio_query = mock_session. \
            query(Audio, Episode). \
            outerjoin(Episode). \
            filter(Audio.owner_user_id == user_id)

        return audios, episodes, mock_audio_query

    @patch.object(audio_operation, 'access_allowed_or_raise')
    @patch('highland.models.Audio.query')
    def test_get_audio_or_assert(self, mock_query, mock_access):
        mock_user, mock_audio = MagicMock(), MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_audio
        mock_query.filter_by.return_value = mock_filter

        result = audio_operation.get_audio_or_assert(
            mock_user, mock_audio.id)

        mock_query.filter_by.assert_called_with(
            owner_user_id=mock_user.id, id=mock_audio.id)
        mock_filter.first.assert_called_with()
        mock_access.assert_called_with(mock_user.id, mock_audio)
        self.assertEqual(result, mock_audio)

    @patch.object(audio_operation, 'access_allowed_or_raise')
    @patch('highland.models.Audio.query')
    def test_get_audio_or_assert_not_found(self, mock_query, mock_access):
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter

        with self.assertRaises(exception.NoSuchEntityError):
            audio_operation.get_audio_or_assert(MagicMock(), 1)
        mock_access.assert_not_called()

    @patch.object(audio_operation, 'access_allowed_or_raise')
    def test_get_audio_url(self, mock_access):
        mock_user, mock_audio = MagicMock(), MagicMock()
        mock_user.identity_id = 'identity_id'
        mock_audio.guid = 'someguid'

        result = audio_operation.get_audio_url(mock_user, mock_audio)

        mock_access.assert_called_with(mock_user.id, mock_audio)
        self.assertEqual(
            '{}/identity_id/someguid'.format(settings.HOST_AUDIO), result)

    def test_access_allowed_or_raise(self):
        mock_audio = MagicMock()
        mock_audio.owner_user_id = 1
        result = audio_operation.access_allowed_or_raise(1, mock_audio)
        self.assertEqual(mock_audio, result)

    def test_access_allowed_or_raise_raise(self):
        mock_audio = MagicMock()
        mock_audio.owner_user_id = 2
        with self.assertRaises(exception.AccessNotAllowedError):
            audio_operation.access_allowed_or_raise(1, mock_audio)
